# Codex Desktop RAG Evaluation Preview

> This preview used the Codex desktop account runtime. The assignment's
> FastAPI/Groq implementation was not changed, and these results are not
> evidence that the deployed API endpoint itself was tested.

- Generated: 2026-09-08T13:08:46.034225+08:00
- Evaluated entries: 27
- Faithfulness: 1.00
- Answer relevance: 0.99
- Correctness: 0.99

## Per-question results

### 1. How can customers track their orders?

**Expected:** Customers can track their orders using the Order Tracking page on the website, or using their order number and registered email address.

**Actual:** Customers can track orders on the website’s Order Tracking page using their order number and registered email address. After shipment, they also receive a tracking number by email or SMS.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Fully supported and accurately includes both tracking methods and the post-shipment notification.

### 2. How long does standard delivery take?

**Expected:** Standard delivery usually takes 3 to 5 business days after shipment.

**Actual:** Standard delivery usually takes 3 to 5 business days after shipment.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Exactly matches the context and expected delivery timeframe.

### 3. How long does express delivery take?

**Expected:** Express delivery usually takes 1 to 2 business days after shipment.

**Actual:** Express delivery usually takes 1 to 2 business days after shipment.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Exactly matches the context and expected delivery timeframe.

### 4. What should a customer do if tracking information has not updated for more than 48 hours?

**Expected:** The customer should contact customer support.

**Actual:** The customer should contact support.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Directly and accurately states the required action.

### 5. What does the order status "Processing" mean?

**Expected:** "Processing" means the warehouse is preparing the order.

**Actual:** “Processing” means the warehouse is preparing the order.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Exactly matches the stated meaning of Processing.

### 6. What does the order status "Shipped" mean?

**Expected:** "Shipped" means the package has been handed over to the courier.

**Actual:** “Shipped” means the package has been handed over to the courier.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Exactly matches the stated meaning of Shipped.

### 7. Within how many days can a customer return an eligible product?

**Expected:** Customers can return eligible products within 30 days of delivery.

**Actual:** Within 30 days of delivery.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Correctly gives the 30-day period measured from delivery.

### 8. What condition must a returned product be in?

**Expected:** Products must be unused and returned in their original packaging, including original accessories, manuals, tags, and invoices when applicable.

**Actual:** The product must be unused and in its original packaging, with original accessories, manuals, tags, and invoices when applicable.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Accurately states all required return-condition details.

### 9. What types of products cannot be returned?

**Expected:** Personalized products, customized products, and certain hygiene products cannot be returned.

**Actual:** Personalized products, customized products, and certain hygiene products cannot be returned.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Exactly identifies the non-returnable product types.

### 10. How does a customer start a return request?

**Expected:** The customer opens the Orders section, selects the order and product, selects "Return Item", and selects a return reason. Photographs may be required for damaged or defective products.

**Actual:** Open the website’s Orders section, select the order containing the product, choose “Return Item,” and select a return reason.

**Scores:** faithfulness 1.00; relevance 0.95; correctness 0.90

**Judge note:** Correctly gives the core return-request steps but omits that photographs may be required for damaged or defective products.

### 11. When does the refund process begin?

**Expected:** The refund process begins once the returned product is received and inspected.

**Actual:** The refund process begins once the returned product is received and inspected.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Exactly states when the refund process begins.

### 12. How long does a refund take to process after a return is inspected?

**Expected:** The refund is normally processed within 5 to 7 business days after the returned product is received and inspected.

**Actual:** A refund is normally processed within 5 to 7 business days after the return is received and inspected.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Accurately gives both the triggering event and processing timeframe.

### 13. Are shipping charges refundable?

**Expected:** Shipping charges are generally non-refundable.

**Actual:** Shipping charges are generally non-refundable.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Exactly matches the stated policy.

### 14. Where is a refund sent if the customer paid by credit card?

**Expected:** The refund will normally be returned to the same credit card that was used for payment.

**Actual:** The refund will normally be returned to the same credit card.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Correctly states that the refund returns to the same credit card.

### 15. Can a customer cancel an order after it has been shipped?

**Expected:** Once an order has been shipped, it cannot normally be cancelled. The customer can request a return after delivery if the product is eligible.

**Actual:** No. Once shipped, an order cannot normally be cancelled. The customer may request a return after delivery if the product is eligible.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Fully captures both the normal cancellation restriction and the return option.

### 16. What should a customer do if they receive a damaged product?

**Expected:** They should report it within 48 hours of delivery and provide photographs showing the damaged product and packaging.

**Actual:** Report it within 48 hours of delivery and provide photographs showing the damaged product and packaging. Keep the original packaging until the issue is resolved.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Fully supported and includes all expected actions plus a relevant packaging instruction.

### 17. What should a customer do if they receive the wrong product?

**Expected:** They should create a return request and select "Wrong Product Received" as the return reason. A replacement may be shipped, or a refund issued if unavailable.

**Actual:** Create a return request and select “Wrong Product Received” as the return reason. You may be asked to provide photographs of the received product.

**Scores:** faithfulness 1.00; relevance 0.90; correctness 0.85

**Judge note:** Correctly explains how to report the wrong product but omits the possible replacement or refund outcomes.

### 18. What should a customer do if an item is missing from their order?

**Expected:** They should contact support and provide the order number and details of the missing item so the support team can check the shipment information.

**Actual:** Contact support and provide the order number and details of the missing item. The support team will check the shipment information.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Exactly matches the required steps and support-team action.

### 19. What payment methods does the store accept?

**Expected:** The store accepts credit cards, debit cards, UPI, and net banking.

**Actual:** The store accepts credit cards, debit cards, UPI, and net banking.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Exactly lists all stated payment methods.

### 20. What should a customer do if a payment failed but the amount was deducted?

**Expected:** If the amount was deducted but the order was not created, the payment will normally be automatically reversed. The customer should contact support if it is not reversed within the expected banking period.

**Actual:** The payment will normally be automatically reversed. Contact support if it is not reversed within the expected banking period.

**Scores:** faithfulness 0.95; relevance 1.00; correctness 0.95

**Judge note:** Correctly states the reversal and escalation guidance, though it does not explicitly mention that the order was not created.

### 21. Is Cash on Delivery available for all products and locations?

**Expected:** Cash on Delivery is available only for eligible products and locations, and some products may not support it.

**Actual:** No. Cash on Delivery is available only for eligible products and locations, and availability is displayed during checkout.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Correctly limits Cash on Delivery to eligible products and locations and adds supported checkout guidance.

### 22. What can cause product prices to change?

**Expected:** Prices may change because of promotions, discounts, seasonal offers, or inventory changes.

**Actual:** Promotions, discounts, seasonal offers, or inventory changes can cause product prices to change.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Exactly lists the stated causes of price changes.

### 23. What happens if a discount coupon has expired?

**Expected:** Expired or invalid coupons cannot be applied.

**Actual:** Expired coupons cannot be applied.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Directly and correctly states that expired coupons cannot be applied.

### 24. Can a customer change their delivery address after the order has shipped?

**Expected:** Once an order has been shipped, the delivery address normally cannot be changed.

**Actual:** Once an order has shipped, the delivery address normally cannot be changed.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Exactly matches the post-shipment address-change policy.

### 25. How can a customer reset a forgotten password?

**Expected:** The customer selects "Forgot Password" on the login page and follows the verification steps sent to their registered email address or mobile number before creating a new password.

**Actual:** Select “Forgot Password” on the login page. A reset link or verification code will be sent to the registered email address or mobile number. Follow the verification steps, then create a new password.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Fully and accurately describes the password-reset process.

### 26. What information should customers never share with customer support?

**Expected:** Customers should never share their account password, card PIN, CVV, or one-time password with customer support.

**Actual:** Customers should never share passwords, card PINs, CVV numbers, or one-time passwords (OTPs).

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Accurately lists all sensitive credentials customers must not share.

### 27. What are the customer support hours?

**Expected:** Customer support is available Monday to Friday from 9 AM to 6 PM.

**Actual:** Customer support is available Monday to Friday from 9 AM to 6 PM.

**Scores:** faithfulness 1.00; relevance 1.00; correctness 1.00

**Judge note:** Exactly matches the stated customer-support hours.
