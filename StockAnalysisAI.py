import pandas as pd
import numpy as np
from datetime import datetime
import json
from io import StringIO

class StockAnalysisAI:
    def __init__(self):
        self.required_fields = ['Date', 'Close']
        
    def validate_data(self, data):
        """Validate input data structure and contents."""
        validation_report = {
            'total_records': 0,
            'required_fields_present': True,
            'date_format_valid': True,
            'close_values_valid': True,
            'errors': []
        }
        
        # Convert input to DataFrame
        if isinstance(data, str):
            try:
                json_data = json.loads(data)
                if isinstance(json_data, dict) and 'data' in json_data:
                    df = pd.json_normalize(json_data['data'])
                else:
                    df = pd.json_normalize(json_data)
            except json.JSONDecodeError:
                try:
                    df = pd.read_csv(StringIO(data))
                except:
                    validation_report['errors'].append("ERROR: Invalid data format. Please provide data in CSV or JSON format.")
                    return None, validation_report
        else:
            validation_report['errors'].append("ERROR: Invalid input type. Please provide string data in CSV or JSON format.")
            return None, validation_report
        
        # Validation checks
        if len(df) == 0:
            validation_report['errors'].append("ERROR: No data records found.")
            return None, validation_report
            
        missing_fields = [field for field in self.required_fields if field not in df.columns]
        if missing_fields:
            validation_report['required_fields_present'] = False
            validation_report['errors'].append(f"ERROR: Missing required field(s): {', '.join(missing_fields)}")
            return None, validation_report
        
        validation_report['total_records'] = len(df)
        return df, validation_report

    def calculate_indicators(self, data):
        """Calculate indicators with focus on percentage change."""
        df = data.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        
        # Calculate percentage change
        df['Pct_Change'] = (df['Close'].pct_change() * 100).round(2)
        
        # Calculate SMA based on number of records
        window_size = min(5, len(df))  # Adaptive window size
        df['SMA'] = df['Close'].rolling(window=window_size).mean().round(2)
        
        return df

    def generate_report(self, data_str):
        """Generate analysis report focusing on percentage changes."""
        # Validate and process data
        data, validation_report = self.validate_data(data_str)
        if data is None:
            return self.format_error_report(validation_report)
            
        results = self.calculate_indicators(data)
        
        # Generate report
        report = "# Stock Market Analysis Report\n\n"
        
        report += "## Data Overview\n"
        report += f"- Total records analyzed: {len(results)}\n"
        report += f"- Date range: {results['Date'].min().strftime('%Y-%m-%d')} to {results['Date'].max().strftime('%Y-%m-%d')}\n\n"
        
        report += "## Record Analysis\n\n"
        
        # Process records
        for idx, row in results.iterrows():
            report += f"### Record {idx + 1} (Date: {row['Date'].strftime('%Y-%m-%d')})\n"
            report += f"Close Price: ${row['Close']:.2f}\n"
            
            if pd.notna(row['Pct_Change']):
                sign = "+" if row['Pct_Change'] > 0 else ""
                report += f"Percentage Change: {sign}{row['Pct_Change']:.2f}%\n"
            else:
                report += "Percentage Change: N/A (First record)\n"
            
            report += "\n"
        
        # Generate indicator summary
        report += "## Indicator Summary\n\n"
        
        # Percentage Change Summary
        pct_changes = results['Pct_Change'].dropna()
        report += "### Percentage Change Statistics\n"
        report += f"- Average Daily Change: {pct_changes.mean():.2f}%\n"
        report += f"- Largest Gain: {pct_changes.max():.2f}%\n"
        report += f"- Largest Decline: {pct_changes.min():.2f}%\n"
        report += f"- Volatility (Std Dev): {pct_changes.std():.2f}%\n\n"
        
        # SMA Summary if applicable
        if len(results) >= 5:
            report += "### 5-Day Simple Moving Average (SMA)\n"
            sma_data = results['SMA'].dropna()
            report += f"- Latest SMA: ${sma_data.iloc[-1]:.2f}\n"
            report += f"- SMA Range: ${sma_data.min():.2f} to ${sma_data.max():.2f}\n\n"
        else:
            report += f"### Simple Moving Average ({min(5, len(results))}-Day)\n"
            report += "- Note: Using shorter window due to limited data points\n"
            sma_data = results['SMA'].dropna()
            if not sma_data.empty:
                report += f"- Latest SMA: ${sma_data.iloc[-1]:.2f}\n"
        
        # Overall trend analysis
        report += "## Overall Trend Analysis\n"
        total_change = ((results['Close'].iloc[-1] - results['Close'].iloc[0]) / results['Close'].iloc[0] * 100).round(2)
        report += f"- Total Price Change: {total_change:.2f}%\n"
        up_days = len(pct_changes[pct_changes > 0])
        down_days = len(pct_changes[pct_changes < 0])
        report += f"- Up Days: {up_days} ({(up_days/len(pct_changes)*100):.1f}%)\n"
        report += f"- Down Days: {down_days} ({(down_days/len(pct_changes)*100):.1f}%)\n"
        
        report += "\n# Feedback Request\n"
        report += "Would you like detailed calculations for any specific record? Please rate this analysis (1-5)."
        
        return report

    def format_error_report(self, validation_report):
        """Format error report when validation fails."""
        report = "# Data Validation Error Report\n\n"
        for error in validation_report['errors']:
            report += f"- {error}\n"
        return report

# Example usage
if __name__ == "__main__":
    # Example data with multiple records
    example_data = """
    {
    "data": [
        {"Date": "2025-08-01", "Close": 800},
        {"Date": "2025-08-02", "Close": 805},
        {"Date": "2025-08-03", "Close": 810},
        {"Date": "2025-08-04", "Close": 815},
        {"Date": "2025-08-05", "Close": 820},
        {"Date": "2025-08-06", "Close": 825},
        {"Date": "2025-08-07", "Close": 830},
        {"Date": "2025-08-08", "Close": 835},
        {"Date": "2025-08-09", "Close": 840},
        {"Date": "2025-08-10", "Close": 845},
        {"Date": "2025-08-11", "Close": 850},
        {"Date": "2025-08-12", "Close": 855},
        {"Date": "2025-08-13", "Close": 860},
        {"Date": "2025-08-14", "Close": 865},
        {"Date": "2025-08-15", "Close": 870}
    ]
    }

    """
    
    analyzer = StockAnalysisAI()
    print(analyzer.generate_report(example_data))