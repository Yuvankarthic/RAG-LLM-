# Data Quality and Governance

## What is Data Quality?

Data quality refers to the state of qualitative or quantitative pieces of information. High-quality data is fit for its intended uses in operations, decision making, and planning. Data is considered high quality if it correctly represents the real-world construct to which it refers.

## Key Dimensions of Data Quality

- **Completeness:** Are all required data attributes present? A product record with a missing price or image is incomplete.
- **Accuracy:** Is the information correct and reliable? An incorrect weight or dimension is an accuracy issue.
- **Consistency:** Is the data uniform across different systems and channels? If a product is "Blue" on the website and "Navy" on the marketplace, the data is inconsistent.
- **Timeliness:** Is the data up-to-date? Information should be updated to reflect changes, such as new product versions or price updates.
- **Uniqueness:** Are there any duplicate records? Every unique product should have a single, master record.
- **Validity:** Does the data conform to a specific format or set of rules? A `gtin` attribute should contain a valid GTIN, not free-form text.

## What is Data Governance?

Data governance is the system of rules, policies, standards, processes, and controls that ensure the effective and efficient use of information in enabling an organization to achieve its goals. In a PIM/MDM context, data governance defines:
- Who can create, read, update, or delete data.
- What data is considered master data.
- How data quality is measured and enforced.
- The workflows for approving changes to data.

Effective data governance is crucial for maintaining high-quality master data and maximizing the value of PIM and MDM solutions.