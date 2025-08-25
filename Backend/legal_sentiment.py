import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import nltk
from nltk.tokenize import sent_tokenize
import re
import os

# Download required NLTK data
nltk.download('punkt', quiet=True)

class LegalSentimentAnalyzer:
    def __init__(self):
        # Initialize FLAN-T5 model and tokenizer
        self.model_name = "google/flan-t5-base"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        
    def preprocess_text(self, text):
        """Clean and preprocess legal text."""
        # Remove excessive whitespace and special characters
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove sensitive information (e.g., specific names, dates)
        text = re.sub(r'\b\d{1,2}/\d{1,2}/\d{4}\b', '[DATE]', text)  # Mask dates
        text = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NAME]', text)  # Mask names
        return text
    
    def analyze_sentiment(self, text):
        """Perform sentiment analysis on a single text segment."""
        prompt = f"Classify the sentiment of this legal text as Positive, Negative, or Neutral: {text}"
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = self.model.generate(**inputs, max_length=10)
        sentiment = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return sentiment.strip()
    
    def summarize_insights(self, sentiments, text_segments):
        """Generate summarized insights from sentiment analysis."""
        total = len(sentiments)
        positive = sum(1 for s in sentiments if s.lower() == 'positive')
        negative = sum(1 for s in sentiments if s.lower() == 'negative')
        neutral = sum(1 for s in sentiments if s.lower() == 'neutral')
        
        summary = (
            f"Sentiment Analysis Summary:\n"
            f"Total Segments Analyzed: {total}\n"
            f"Positive Segments: {positive} ({positive/total*100:.1f}%)\n"
            f"Negative Segments: {negative} ({negative/total*100:.1f}%)\n"
            f"Neutral Segments: {neutral} ({neutral/total*100:.1f}%)\n\n"
            f"Key Observations:\n"
        )
        
        if positive > negative and positive > neutral:
            summary += "- The overall tone of the document is predominantly positive, suggesting favorable outcomes or opinions."
        elif negative > positive and negative > neutral:
            summary += "- The overall tone is predominantly negative, indicating potential issues or unfavorable sentiments."
        else:
            summary += "- The document maintains a balanced or neutral tone, with no strong positive or negative bias."
        
        return summary
    
    def process_file(self, file_path):
        """Process a single text or CSV file and perform sentiment analysis."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")
        
        results = []
        text_segments = []
        
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            if 'text' not in df.columns:
                raise ValueError("CSV file must contain a 'text' column.")
            texts = df['text'].tolist()
        else:
            with open(file_path, 'r', encoding='utf-8') as file:
                texts = [file.read()]
        
        for text in texts:
            # Preprocess and split into sentences
            cleaned_text = self.preprocess_text(text)
            sentences = sent_tokenize(cleaned_text)
            
            for sentence in sentences:
                if len(sentence.strip()) > 10:  # Ignore very short sentences
                    sentiment = self.analyze_sentiment(sentence)
                    results.append({'text': sentence, 'sentiment': sentiment})
                    text_segments.append(sentence)
        
        # Generate summary
        sentiments = [result['sentiment'] for result in results]
        summary = self.summarize_insights(sentiments, text_segments)
        
        # Create output DataFrame
        output_df = pd.DataFrame(results)
        return output_df, summary

def main():
    analyzer = LegalSentimentAnalyzer()
    input_file = input("Enter the path to the legal document (text or CSV): ")
    
    try:
        output_df, summary = analyzer.process_file(input_file)
        
        # Save results to CSV
        output_file = "sentiment_analysis_results.csv"
        output_df.to_csv(output_file, index=False)
        print(f"\nResults saved to {output_file}")
        
        # Print summary
        print("\n" + summary)
        
        # Print sample results
        print("\nSample Results (first 5 segments):")
        print(output_df.head().to_string(index=False))
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()