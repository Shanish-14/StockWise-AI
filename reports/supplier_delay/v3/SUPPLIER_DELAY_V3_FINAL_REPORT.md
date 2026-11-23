
# StockWise AI
# Supplier Delay Prediction – V3 Final Evaluation Report

## 1. Project Overview

Supplier Delay Prediction is Feature 3 of StockWise AI.

The objective is to predict whether a grocery supplier order will be delayed before its expected delivery.

V3 uses a simulated grocery supply-chain dataset containing 50,000 orders.

**Important:** The dataset is synthetic. It does not contain actual supermarket or supplier transaction records. Results represent experimental model performance on simulated data only.

## 2. Dataset Description

- Total records: 50,000
- Stores: 20
- Suppliers: 30
- Products: 200
- Product categories: 8
- Date range: January 2024 – December 2025
- Target: `is_delayed`

The dataset includes order quantity, supplier reliability, delivery distance, capacity utilization, promised delivery days, transport risk and other order characteristics.

## 3. Data Quality Inspection

- Missing values: 0
- Duplicate order IDs: 0
- Duplicate rows: 0
- Delivery date and delay target inconsistencies: 0

The dataset passed the implemented data-quality checks.

## 4. Model Development

Three classification algorithms were evaluated:

1. Logistic Regression
2. Random Forest
3. Gradient Boosting

A chronological split based on unique order dates was used.

| Split | Records |
|---|---:|
| Training | 34,979 |
| Validation | 7,565 |
| Final Test | 7,456 |

The Random Forest model was selected using validation ROC AUC.

Validation ROC AUC: 0.5700

The final test dataset was kept separate during model selection.

## 5. Final Test Evaluation

The selected Random Forest pipeline was evaluated on the untouched final test dataset using a threshold of 0.50.

| Metric | Result |
|---|---:|
| Accuracy | 47.83% |
| Precision | 29.80% |
| Recall | 66.91% |
| F1 Score | 41.24% |
| ROC AUC | 56.11% |
| PR AUC | 31.87% |

### Confusion Matrix

| | Predicted On Time | Predicted Delayed |
|---|---:|---:|
| Actual On Time | 2,201 | 3,215 |
| Actual Delayed | 675 | 1,365 |

The model identified 1,365 delayed orders but incorrectly flagged 3,215 on-time orders.

## 6. Threshold Analysis

Threshold analysis was conducted using validation predictions only.

The best F1 score was obtained at threshold 0.45.

| Metric | Threshold 0.45 |
|---|---:|
| Accuracy | 34.54% |
| Precision | 25.48% |
| Recall | 87.58% |
| F1 Score | 39.48% |

Although recall increased, false positives also increased substantially.

The threshold was not applied to the final test predictions. The final test evaluation at 0.50 remains unchanged.

## 7. Feature Importance

The validation feature analysis identified supplier reliability, order quantity, product category, transport risk and capacity utilization as useful predictive signals.

Permutation importance showed that product ID contributed very little to validation predictive performance.

These findings describe the simulated dataset and should not be interpreted as verified real-world grocery supply-chain relationships.

## 8. Limitations

1. The dataset is synthetically generated, not collected from real grocery businesses.
2. The model's predictive performance is weak.
3. False positive predictions are high.
4. Model performance may not generalize to real suppliers and stores.
5. The simulated data may contain patterns that do not represent actual supply-chain behaviour.
6. The model is not suitable for production deployment.

## 9. Final Conclusion

Supplier Delay Prediction V3 demonstrates an experimental machine-learning workflow for grocery supplier-to-store delivery risk prediction.

The project includes synthetic dataset generation, data inspection, chronological splitting, model comparison, feature analysis, final test evaluation and threshold analysis.

However, the final test results show limited predictive ability.

Therefore, V3 is retained as an experimental prototype and requires real-world delivery records and further validation before practical deployment.

**Project Status: Experimental Prototype – Evaluation Completed**
