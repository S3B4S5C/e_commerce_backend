from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from products.models import Product
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem, PaymentDetail, ShippingMethod, OrderStatus
from users.models import UserAccount
from django.utils import timezone
import requests
from django.conf import settings


class VoiceAssistantView(APIView):
    permission_classes = [IsAuthenticated]
    intents = ["buscar", "agregar", "ver_carrito", "realizar_pedido"]

    def post(self, request):
        user_input = request.data.get("text", "")
        user_email = request.user
        try:
            user = UserAccount.objects.get(email=user_email)
        except UserAccount.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)

        user_id = user.id
        session = request.session 
        print(session) # log
        confirm = user_input in ["sí", "si", "confirmar", "ok", "dale", "hazlo"]
        print(confirm) # log
        if session.get("pending_intent") and confirm:
            intent = session.pop("pending_intent")
            data = session.pop("pending_data", None)
            session.modified = True
            print(f"Intent: {intent}, Data: {data}") # log
        else:
            groq_response = self.ask_groq(user_input)
            intent, data = self.parse_intent(groq_response)
            print(f"elseIntent: {intent}, Data: {data}") # log

        # Si la intención requiere confirmación
        if intent in ["buscar", "agregar", "realizar_pedido"] and not confirm:
            session["pending_intent"] = intent
            session["pending_data"] = data
            session.modified = True
            mensajes = {
                "buscar": f"¿Querés que busque productos relacionados con '{data}'?",
                "agregar": f"¿Querés que agregue '{data}' al carrito?",
                "realizar_pedido": "¿Querés que procese tu pedido ahora?"
            }
            return Response({"result": mensajes[intent]})

        if intent == "buscar":
            productos = Product.objects.filter(
                name__icontains=data or "",
            ) | Product.objects.filter(
                category__icontains=data or "",
            ) | Product.objects.filter(
                brand__icontains=data or ""
            )
            productos_serializados = [{"name": p.name, "price": p.price, "category": p.category, "brand": p.brand} for p in productos]
            return Response({"result": productos_serializados})

        elif intent == "agregar":
            producto = Product.objects.filter(name__icontains=data).first()
            if not producto:
                return Response({"result": f"No encontré un producto con el nombre '{data}'."})

            cart, _ = Cart.objects.get_or_create(user_id=user_id, deleted_at__isnull=True, defaults={"total_price": 0})
            item, created = CartItem.objects.get_or_create(cart=cart, product=producto)
            item.quantity_product = (item.quantity_product or 0) + 1
            item.save()
            cart.total_price += producto.price
            cart.save()
            return Response({"result": f"Agregado {producto.name} al carrito."})

        elif intent == "ver_carrito":
            cart = Cart.objects.filter(user_id=user_id, deleted_at__isnull=True).first()
            if not cart:
                return Response({"result": "Tu carrito está vacío."})
            items = CartItem.objects.filter(cart=cart)
            productos = [{"producto": i.product.name, "cantidad": i.quantity_product} for i in items]
            return Response({"result": productos})

        elif intent == "realizar_pedido":
            cart = Cart.objects.filter(user_id=user_id, deleted_at__isnull=True).first()
            if not cart:
                return Response({"result": "No hay carrito para procesar."})
            user = UserAccount.objects.get(id=user_id)
            items = CartItem.objects.filter(cart=cart)

            payment = PaymentDetail.objects.create(
                state="pagado", provider="manual", created_at=timezone.now(), modified_at=timezone.now()
            )
            shipping = ShippingMethod.objects.first()
            status = OrderStatus.objects.first()

            order = Order.objects.create(
                user=user,
                payment_detail=payment,
                shipping_method=shipping,
                status=status,
                date=timezone.now().date(),
                time=timezone.now().time(),
                total_price=cart.total_price,
                created_at=timezone.now(),
                modified_at=timezone.now()
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity_product,
                    created_at=timezone.now(),
                    modified_at=timezone.now()
                )

            cart.deleted_at = timezone.now()
            cart.save()

            return Response({"result": f"Pedido realizado por un total de ${order.total_price}."})

        return Response({"result": "No entendí tu solicitud."})

    def ask_groq(self, text):
        intents = ["buscar", "agregar", "ver_carrito", "realizar_pedido"]  # <- debes colocarla aquí

        prompt = (
            "Sos un asistente de compras para un e-commerce.\n"
            "Solo podés responder con una intención válida de esta lista:\n"
            f"{', '.join(intents)}\n\n"
            "**Formato obligatorio:** `intención:parámetro`\n"
            "Ejemplos válidos:\n"
            "- buscar:auriculares\n"
            "- agregar:Smart TV\n"
            "- ver_carrito\n"
            "- realizar_pedido\n\n"
            "**Reglas:**\n"
            "- No agregues ningún texto adicional.\n"
            "- Si la intención no necesita parámetro (como 'ver_carrito' o 'realizar_pedido'), igual responde en el formato pero sin parámetro: `ver_carrito`\n"
            "- NO inventes nuevas intenciones. Solo usá las de la lista.\n"
        )

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text}
                ]
            }
        )

        
        content = response.json()["choices"][0]["message"]["content"]
        print(content)
        return content

    def parse_intent(self, text):
        if ":" in text:
            intent, param = text.split(":", 1)
            return intent.strip(), param.strip()
        return text.strip(), None
