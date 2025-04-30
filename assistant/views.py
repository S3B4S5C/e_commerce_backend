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
            return Response({'result': 'Usuario no encontrado'}, status=404)

        user_id = user.id

        groq_response = self.ask_groq(user_input)
        intent, data = self.parse_intent(groq_response)

        if intent == "buscar":
            return Response({"result": f"Buscando productos relacionados con '{data}'."})

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
            return Response({"result": f"Se agregó '{producto.name}' al carrito."})

        elif intent == "ver_carrito":
            cart = Cart.objects.filter(user_id=user_id, deleted_at__isnull=True).first()
            if not cart:
                return Response({"result": "Tu carrito está vacío."})
            items = CartItem.objects.filter(cart=cart)
            if not items:
                return Response({"result": "Tu carrito está vacío."})
            resumen = ", ".join([f"{i.quantity_product} x {i.product.name}" for i in items])
            return Response({"result": f"Tu carrito contiene: {resumen}."})

        elif intent == "realizar_pedido":
            cart = Cart.objects.filter(user_id=user_id, deleted_at__isnull=True).first()
            if not cart:
                return Response({"result": "No hay carrito para procesar."})
            items = CartItem.objects.filter(cart=cart)
            if not items:
                return Response({"result": "Tu carrito está vacío."})

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

            return Response({"result": f"Tu pedido fue realizado correctamente por un total de ${order.total_price}."})

        return Response({"result": "No entendí tu solicitud."})

    def ask_groq(self, text):
        intents = ["buscar", "agregar", "ver_carrito", "realizar_pedido"]  # <- debes colocarla aquí

        prompt = (
            "Sos un asistente de voz para un e-commerce.\n"
            "Tu tarea es identificar la intención del usuario en base a su mensaje.\n"
            "Solo podés responder con una de las siguientes intenciones válidas:\n"
            "- buscar\n"
            "- agregar\n"
            "- ver_carrito\n"
            "- realizar_pedido\n\n"
            "**Formato de respuesta obligatorio:**\n"
            "Solo devolvé la intención y, si corresponde, el parámetro, separados por dos puntos, sin texto adicional.\n\n"
            "**Ejemplos válidos:**\n"
            "- buscar:auriculares\n"
            "- agregar:Smart TV\n"
            "- ver_carrito\n"
            "- realizar_pedido\n\n"
            "**Reglas estrictas:**\n"
            "- NO expliques nada.\n"
            "- NO devuelvas texto adicional.\n"
            "- NO uses comillas.\n"
            "- NO inventes nuevas intenciones.\n"
            "- Si la intención no requiere parámetro (como 'ver_carrito' o 'realizar_pedido'), solo devolvé la intención.\n"
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
