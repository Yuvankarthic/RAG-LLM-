# Product Attributes

## What are Product Attributes?

Product attributes are the characteristics that define a product. They are the specific details that describe what a product is, what it does, and its features. Attributes provide structured information that helps customers find, compare, and understand products.

## Types of Attributes

- **Descriptive Attributes:** These describe the features and benefits of a product. Examples include:
  - `short_description`: A brief, engaging summary.
  - `long_description`: A detailed explanation of the product's features and benefits.
  - `color`: The primary color of the product (e.g., "Blue", "Red").
  - `material`: The primary material used (e.g., "Cotton", "Stainless Steel").

- **Technical/Physical Attributes:** These relate to the physical dimensions and technical specifications of a product. Examples include:
  - `height`, `width`, `depth`: The dimensions of the product.
  - `weight`: The weight of the product.
  - `voltage`: The electrical voltage requirements.

- **Logistical Attributes:** These are used for supply chain and inventory management. Examples include:
  - `sku`: Stock Keeping Unit, a unique internal identifier.
  - `gtin`: Global Trade Item Number, such as a UPC or EAN.
  - `country_of_origin`: The country where the product was manufactured.

## Mandatory vs. Optional Attributes

- **Mandatory Attributes:** These are essential pieces of information required to list or sell a product. Without them, a product record is considered incomplete. For example, `sku`, `product_name`, and `price` are almost always mandatory.
- **Optional Attributes:** These provide additional, enriching information that improves the customer experience but are not strictly required. For example, `secondary_color` or `care_instructions` might be optional. The set of mandatory attributes can change depending on the sales channel.