# Numeo AI Knowledge Base

This file contains reference Q&A content about Numeo AI products and services.
It can be embedded and stored in pgvector to support Retrieval-Augmented Generation (RAG)
for answering customer emails.

---

## General Information

**Q: What is Numeo AI?**  
A: Numeo AI builds AI-powered agents that automate tasks in the freight and logistics industry.  
These agents help carriers and dispatchers manage load booking, document verification,
status updates, and broker communications.

**Q: Who typically uses Numeo AI?**  
A: Carriers, owner-operators, freight dispatchers, and logistics companies use Numeo AI to
reduce manual work, save time, and increase efficiency in operations.

---

## Products and Features

**Q: What are Numeo AI’s main products?**  
A: Key products include:

- **AI Broker** – negotiates rates and manages broker communications.
- **Spot Finder** – searches and recommends freight loads.
- **Updater Agent** – provides automatic load status updates.
- **VoiceFlow Agent** – handles phone calls with brokers and partners.
- **Document Intelligence** – processes rate confirmations, Bills of Lading (BOLs),
  and Proof of Delivery (PODs).

**Q: Can Numeo AI integrate with load boards?**  
A: Yes. Numeo AI integrates with load boards like DAT and Truckstop to help
automate the search and booking of freight loads.

**Q: How does Numeo AI handle documents?**  
A: Numeo AI extracts key details from logistics documents (e.g., order IDs, rates,
carrier details) using AI-powered document intelligence, reducing manual entry errors.

---

## Operations and Support

**Q: How does Numeo AI improve dispatch operations?**  
A: By automating repetitive tasks like broker calls, load matching, and paperwork checks,
dispatchers can focus on decision-making and managing more loads with less effort.

**Q: How secure is my data with Numeo AI?**  
A: All data is processed under strict security protocols. Sensitive documents
and communications are handled with encryption and stored securely.

**Q: What happens if the AI agent cannot answer my question?**  
A: The system will mark the email as _unhandled_ with **high priority**
so that a support agent can follow up.

---

## Refunds and Orders (Demo Behavior for Agent)

**Q: How long does it take to process a refund?**  
A: Refunds are processed within **3 business days** after the order ID is validated.

**Q: What if I don’t include an order ID in my refund request?**  
A: The system will automatically reply asking for the missing order ID.

**Q: What if I send an invalid order ID?**  
A: The system will respond that the order ID is invalid. If the same invalid ID is sent again,
it will be logged in the _not found refund requests_ table for review.

---
