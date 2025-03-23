import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

# Load the processed data
data_dict = pickle.load(open('./data.pickle', 'rb'))  

# Fix the data array by padding/truncating all samples to a uniform length
data = data_dict['data']
labels = data_dict['labels']

# Define the fixed feature size (e.g., 21 landmarks * 2 coordinates)
MAX_LANDMARKS = 42  # Adjust if needed

# Standardize the shape of the data
processed_data = []
for sample in data:
    if len(sample) < MAX_LANDMARKS:
        # Pad with zeros if the sample is too short
        sample.extend([0] * (MAX_LANDMARKS - len(sample)))
    elif len(sample) > MAX_LANDMARKS:
        # Truncate if the sample is too long
        sample = sample[:MAX_LANDMARKS]
    processed_data.append(sample)

# Convert the standardized data into a NumPy array
data = np.asarray(processed_data, dtype=np.float32)
labels = np.asarray(labels)

# Ensure the shape is consistent
if len(data.shape) != 2:
    raise ValueError("Data shape is inconsistent. Ensure all samples have the same number of features.")

# Split the data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(
    data, labels, test_size=0.2, shuffle=True, stratify=labels
)

# Initialize and train the Random Forest classifier
model = RandomForestClassifier()
model.fit(x_train, y_train)

# Make predictions on the test set
y_predict = model.predict(x_test)

# Calculate the accuracy
score = accuracy_score(y_predict, y_test)
print(f'{score * 100:.2f}% of samples were classified correctly!')

# Save the trained model to a file
with open('model.p', 'wb') as f:
    pickle.dump({'model': model}, f)

print("Model saved successfully as 'model.p'.")
