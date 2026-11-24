# StockWise AI – Feature 4: Inter-Store Stock Transfer Optimization

## 1. Introduction

Inter-Store Stock Transfer Optimization is the fourth feature of StockWise AI. Its purpose is to identify stores that may have excess inventory and stores that may need additional inventory of the same product.

Instead of purchasing additional stock immediately, the system identifies potential donor stores and recommends transferring stock between stores.

This feature combines historical retail sales and stock availability indicators with a simulated inventory layer.

## 2. Dataset Description

The feature uses the FreshRetailNet retail dataset, which contains historical retail sales and stock availability information.

**Dataset details:**
- Original dataset size: 4,500,000 records.
- Columns used: `store_id`, `product_id`, `dt`, `sale_amount`, `stock_hour6_22_cnt`.
- Sample used in the initial prototype: 18,000 records.
- Stores represented in the sample: 21.
- Products represented in the sample: 143.

The sample contains products sold across multiple stores, with differences in their recorded stock availability.

**Important:** `stock_hour6_22_cnt` represents a stock availability-hours indicator. It is not a physical inventory quantity.

## 3. Methodology

The feature follows these steps:

1. Load historical retail sales and availability data.
2. Calculate average daily sales for each store-product combination.
3. Calculate average stock availability hours.
4. Estimate daily demand using a documented simulation assumption.
5. Generate simulated inventory quantities.
6. Calculate simulated inventory surplus and shortage.
7. Identify potential donor and receiver stores.
8. Match donor and receiver stores for the same product.
9. Calculate recommended transfer quantities.
10. Validate the recommendations.

## 4. Simulated Inventory Layer

The original retail dataset does not contain actual physical inventory quantities or inter-store transfer records.

Therefore, a simulated inventory layer was introduced.

The prototype uses these assumptions:

- Sales-to-simulated-units multiplier: 10.
- Target inventory coverage: 2 days.
- Simulated inventory coverage: randomly generated between 0.5 and 5 days.
- Random seed: 42.
- Minimum donor availability threshold: 4 hours.
- Maximum receiver availability threshold: 6 hours.

These are experimental assumptions used to demonstrate the transfer workflow. They are not measured supermarket inventory policies or industry standards.

## 5. Transfer Recommendation Logic

A store is considered a potential donor when:

- Its average availability is at least 4 hours.
- Its simulated inventory exceeds its simulated target inventory.

A store is considered a potential receiver when:

- Its average availability is at most 6 hours.
- Its simulated inventory is below its target inventory.
- Its estimated daily demand is positive.

The system matches donors and receivers for the same product.

Transfer quantity is limited by both the donor's remaining simulated surplus and the receiver's remaining simulated shortage.

The engine updates these remaining quantities after every recommendation to prevent allocating the same simulated stock more than once.

## 6. Experimental Results

The initial prototype generated the following results:

| Metric | Result |
|---|---:|
| Sample records | 18,000 |
| Store-product combinations | 216 |
| Transfer recommendations | 4 |
| Total simulated transfer quantity | 23 units |
| Validation checks passed | 7 out of 7 |
| Validation failures | 0 |

### Example recommendations

| Product | Donor Store | Receiver Store | Simulated Transfer |
|---|---:|---:|---:|
| 834 | 0 | 157 | 15 |
| 74 | 434 | 305 | 6 |
| 291 | 668 | 678 | 1 |
| 740 | 0 | 157 | 1 |

These recommendations are outputs of the experimental simulation, not actual stock transfer records.

## 7. Validation

Seven validation checks were performed:

1. No store transfers stock to itself.
2. No duplicate donor-receiver-product recommendations.
3. All transfer quantities are positive.
4. Donor transfers do not exceed simulated surplus.
5. Receiver transfers do not exceed simulated shortage.
6. All donor inventory references exist.
7. All receiver inventory references exist.

**Validation result: PASSED – 7/7 checks.**

## 8. Limitations

- Inventory quantities are simulated, not actual supermarket stock counts.
- The prototype uses an 18,000-record sample rather than the complete 4.5-million-record dataset.
- Transfer costs, transportation time, vehicle capacity and distance constraints are not included.
- Product expiry and storage conditions are not considered in the transfer decision.
- The thresholds and inventory assumptions require real business data and testing before operational use.
- The validation checks mathematical consistency of the simulated recommendations, not real-world business performance.

## 9. Conclusion

The Inter-Store Stock Transfer Optimization feature demonstrates how historical retail sales and stock availability information can support potential stock redistribution between stores.

The prototype successfully generated four transfer recommendations and passed all seven validation checks.

It provides an experimental foundation for a future inventory optimization system. Further work using actual inventory quantities, transfer costs, logistics information and larger-scale data is required before production deployment.

**Feature status:** Experimental prototype implemented and validated against simulated inventory assumptions.