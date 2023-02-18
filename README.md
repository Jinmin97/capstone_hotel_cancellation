### Problem statement

Significant number of hotel reservations are called off due to cancellations or no shows. The typical reasons for cancellations include change of plans, scheduling conflicts, change of mind, etc. This is often made easier by the option to do so free of charge or preferably at a low cost which is beneficial to hotel guests, but it is a less desirable and possibly revenue-diminishing factor for hotels to deal with.

Deliverable: To build a website for hotel’s staff to predict whether a customer will cancel the booking or not so that they are able to reduce loss by allowing more booking and at the same time ensuring the rooms are not overbooked.

### Dataset description

The dataset is taken from Kaggle [here](https://www.kaggle.com/datasets/ahsan81/hotel-reservations-classification-dataset)

### The Modelling Process

We will be comparing three different classification algorithms: **Logistic Regression**, **Random Forest Classification** and **XGBoost**

After tuning the hyperparameters for each algorithms, the XGBoost classifier yielded the best results, with a F1 score of ~75%. 

Modelling Process: 

1. Generate the classification models. Within this process, we will be making use of:
    - train-test split
    - cross-validation / grid searching for hyperparameters


2. Evaluate our models
    - consider the evaluation metrics
    - consider the baseline score

### Cost Benefit Analysis 

Cost: Compensation to the customer => one night's stay + transportation cost to the new property = $103 + $20 = $123

Benefit: Additional revenue => Cost of an additional room = $103

**Model was used**
The worst case scenario in using the model would be that the hotel is overbooked. Assuming there are x rooms, the hotel will be earning $103 * x = $103x. When we factor in the compensation the hotel needs to pay to those they did not honour the rooms to, (0.15x based on 1-precision (also known as the % of time the model will predict that customer will cancel when in fact they did not)), the total revenue is $103x - ($123)*0.15x = $84.55x.

**Model was not used**
If we did not use the model, based on global average occupancy rates, the hotel would be operating at 65% - 80% capacity ([source]: https://hoteltechreport.com/news/occupancy-rate)). For simplity, we will take the occupancy rate as 75%. The total revenue would be $103*0.75x = $77.25x

**Revenue comparison**
With a precision of 85%, the XGBoost model will generate an increase of ~9.5% revenue

    
### Conclusions/Recommendations

**Conclusion:**


**Recommendations:**

