from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder


encoder = HuggingFaceEncoder(name="sentence-transformers/all-MiniLM-L6-v2")


faq = Route(
    name="faq",
    utterances=[
        "What is the return policy of the products?",
        "Do I get discount with the HDFC credit card?",
        "How can I track my order?",
        "What payment methods are accepted?",
        "How long does it take to process a refund?",
        "Can I pay using UPI?",
        "Is cash on delivery available?",
        "Tell me how I can return an item.",
        "Do you accept credit cards?",
        "What's the refund process?",
        "How to cancel my order?"
    ]
)


sql = Route(
    name="sql",
    utterances=[
        "I want to buy Nike shoes that have 50% discount.",
        "Are there any shoes under Rs. 3000?",
        "Do you have formal shoes in size 9?",
        "Are there any Puma shoes on sale?",
        "What is the price of Puma running shoes?",
        "Show me Adidas sneakers for men.",
        "Any black leather shoes in stock?",
        "List all discounted products",
        "I want shoes for women under 2000",
        "Find me red sneakers with offers"
    ]
)


router = SemanticRouter(
    routes=[faq, sql],
    encoder=encoder,

    auto_sync='local'
)


router.sync('local', force=True)


if __name__ == '__main__':
    print(router("What is the return policy of the products?").name)
    print(router("Pink Puma shoes in price range 5000 to 1000").name)

