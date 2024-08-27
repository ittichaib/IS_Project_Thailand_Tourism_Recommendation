import numpy as np
import re
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GRU, Dense, Dropout, Attention, Concatenate
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from sklearn.metrics import accuracy_score, classification_report
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.regularizers import l2
import shap

# Advanced text cleaning
def advanced_clean_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = re.sub(r'[^a-z\s]', '', text)  # Remove special characters
    text = re.sub(r'\b(u|ur|b4)\b', 'you', text)  # Replace common abbreviations
    words = word_tokenize(text)
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return ' '.join(words)

# Apply the advanced cleaning function
review_df['cleaned_review'] = review_df['review'].apply(advanced_clean_text)

# Tokenize and convert reviews to sequences
tokenizer = Tokenizer(num_words=20000)
tokenizer.fit_on_texts(review_df['cleaned_review'])
X_sequences = tokenizer.texts_to_sequences(review_df['cleaned_review'])

# Pad sequences to ensure equal length input for the GRU model
max_sequence_length = 100  # Adjust based on your data
X_pad = pad_sequences(X_sequences, maxlen=max_sequence_length)

# Convert the labels to integers
label_mapping = {'negative': 0, 'neutral': 1, 'positive': 2}
y = review_df['sentiment'].map(label_mapping)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_pad, y, test_size=0.2, random_state=42)

# Create the embedding matrix from the Word2Vec model
embedding_dim = word2vec_model.vector_size
word_index = tokenizer.word_index
embedding_matrix = np.zeros((len(word_index) + 1, embedding_dim))

for word, i in word_index.items():
    if word in word2vec_model.wv:
        embedding_matrix[i] = word2vec_model.wv[word]

# Build the GRU model with advanced regularization and attention
model = Sequential()
model.add(Embedding(input_dim=len(word_index) + 1,
                    output_dim=embedding_dim,
                    weights=[embedding_matrix],
                    input_length=max_sequence_length,
                    trainable=True))  # Fine-tuning the embeddings

# GRU layers with attention
gru_output = GRU(units=128, return_sequences=True)(model.output)
attention = Attention()([gru_output, gru_output])
context_vector = Concatenate()([gru_output, attention])
context_vector = GRU(units=128)(context_vector)
context_vector = Dropout(0.5)(context_vector)

# Dense layers with L2 regularization
dense_output = Dense(units=64, activation='relu', kernel_regularizer=l2(0.001))(context_vector)
dense_output = Dropout(0.5)(dense_output)
output = Dense(units=3, activation='softmax')(dense_output)  # 3 classes: negative, neutral, positive

model = tf.keras.Model(inputs=model.input, outputs=output)

# Compile the model with class weights and L2 regularization
class_weights = {0: 1.0, 1: 2.0, 2: 1.5}  # Adjust these based on actual class distribution

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Early stopping
early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

# Train the model
history = model.fit(X_train, y_train,
                    epochs=10,
                    batch_size=64,
                    validation_data=(X_test, y_test),
                    class_weight=class_weights,
                    callbacks=[early_stopping])

# Evaluate the model on test data
y_pred = model.predict(X_test)
y_pred_classes = y_pred.argmax(axis=1)

# Calculate accuracy and classification report
accuracy = accuracy_score(y_test, y_pred_classes)
print(f'Accuracy: {accuracy:.4f}')
print(classification_report(y_test, y_pred_classes, target_names=['negative', 'neutral', 'positive']))

# SHAP values for interpretability
explainer = shap.DeepExplainer(model, X_train[:100])  # Simplified example with first 100 samples
shap_values = explainer.shap_values(X_test[:10])  # Explain predictions for 10 samples
shap.summary_plot(shap_values, X_test[:10])

# Optionally, compare predicted sentiment with original ratings as before
predicted_sentiment = pd.Series(y_pred_classes).map({0: 'negative', 1: 'neutral', 2: 'positive'})
comparison_df = pd.DataFrame({
    'original_rating': y_test.map({0: 'negative', 1: 'neutral', 2: 'positive'}),
    'predicted_sentiment': predicted_sentiment
})

print(comparison_df.head(20))