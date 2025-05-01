import pandas as pd
import yfinance as yf
import time
import datetime

def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    sp500_table = pd.read_html(url)[0]
    tickers = sp500_table['Symbol'].tolist()
    return [ticker.replace('.', '-') for ticker in tickers]

def download_in_batches(tickers, start, end, batch_size=50, pause_seconds=5, max_retries=3):
    all_data = pd.DataFrame()

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        print(f"Downloading batch {i//batch_size + 1} of {len(tickers)//batch_size + 1}: {batch}")

        success = False
        retries = 0
        while not success and retries < max_retries:
            try:
                data = yf.download(batch, start=start, end=end)['Adj Close']
                all_data = pd.concat([all_data, data], axis=1)
                success = True
            except Exception as e:
                retries += 1
                print(f"Retry {retries}/{max_retries} for batch due to error: {e}")
                time.sleep(pause_seconds)

        if not success:
            print(f"Failed to download batch {i//batch_size + 1}: {batch}")

        time.sleep(pause_seconds)

    return all_data

def compute_correlation_matrix(price_df):
    print("Calculating daily returns...")
    daily_returns = price_df.pct_change().dropna()
    print("Computing correlation matrix...")
    return daily_returns.corr()

def main():
    start_date = "2024-01-01"
    end_date = "2024-12-31"

    print("Fetching S&P 500 tickers...")
    tickers = get_sp500_tickers()

    print("Downloading historical price data...")
    price_df = download_in_batches(tickers, start_date, end_date)

    if price_df.empty:
        print("No price data downloaded. Try reducing batch size or date range.")
        return

    correlation_matrix = compute_correlation_matrix(price_df)
    correlation_matrix.to_csv("sp500_correlation_matrix.csv")
    print("Correlation matrix saved to sp500_correlation_matrix.csv")

if __name__ == "__main__":
    main()
