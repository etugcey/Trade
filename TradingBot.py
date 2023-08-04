import backtrader as bt  # Import the backtrader library for backtesting
import configparser     # Import the configparser library for reading config file
import rarfile          # Import the rarfile library for extracting RAR archives
import getpass          # Import the getpass library for securely entering passwords
import os               # Import the os library for file operations
from binance.client import Client  # Import the Binance API client for fetching historical data

def extract_config(rar_path, password):
    """
    Extracts the content of 'config.ini' from the password-protected RAR archive.
    
    :param rar_path: Path to the password-protected RAR archive.
    :param password: Password for the RAR archive.
    :return: Content of 'config.ini' as a string.
    """
    with rarfile.RarFile(rar_path) as rar:
        rar.setpassword(password.encode('utf-8'))
        with rar.open('config.ini') as config_file:
            config_content = config_file.read()
    return config_content.decode('utf-8')

# Prompt user for RAR password
rar_password = getpass.getpass("Enter password for the RAR archive: ")

# Extract API keys from the config.ini within the password-protected RAR archive
config_content = extract_config('protected_config.rar', rar_password)

# Parse API keys from config.ini
config = configparser.ConfigParser()
config.read_string(config_content)

API_KEY = config.get('binance', 'api_key')
API_SECRET = config.get('binance', 'api_secret')
# Remove the extracted config.ini file
os.remove('config.ini')

class SimpleStrategy(bt.Strategy):
    """
    Simple trading strategy based on a Simple Moving Average (SMA) crossover.
    """
    params = (
        ('sma_period', 20),  # Parameter for the Simple Moving Average (SMA) period in days
    )

    def __init__(self):
        # Create the Simple Moving Average indicator with the specified SMA period
        self.sma = bt.indicators.SimpleMovingAverage(self.data, period=self.params.sma_period)

    def next(self):
        """
        Executes on each new trading day.
        If not in a position, checks for a long entry signal and places a buy order.
        If in a long position, checks for a long exit signal and closes the position.
        """
        if not self.position:  # If no position, check for a long entry signal
            if self.data.close[0] > self.sma[0]:  # Compare the current closing price with the SMA value
                self.buy()  # Place a buy order to enter a long position
        elif self.data.close[0] < self.sma[0]:  # If in a long position, check for a long exit signal
            self.close()  # Close the current long position

# Backtesting and Live Trading
if __name__ == '__main__':
    mode = input("Choose mode (backtest/live): ").strip().lower()

    cerebro = bt.Cerebro()  # Create a backtesting engine

    if mode == 'backtest':
        # Get Binance historical data
        client = Client(API_KEY, API_SECRET)
        klines = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1DAY)
        data = bt.feeds.PandasData(dataname=klines, openinterest=None, datetime=0, open=1, high=2, low=3, close=4, volume=5)

        cerebro.adddata(data)  # Add the data feed to the backtesting engine
        cerebro.addstrategy(SimpleStrategy)  # Add the trading strategy to the backtesting engine
        cerebro.broker.set_cash(1000)  # Set your initial capital to 1000 USDT
        cerebro.broker.set_coc(True)  # Close on close (no intra-candle operations)
        cerebro.broker.setcommission(commission=0.001)  # Set the Binance trading fee to 0.1% (0.001 as a fraction)

        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        # Print the starting portfolio value before running the backtest

        cerebro.run()  # Run the backtest
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
        # Print the final portfolio value after the backtest

        cerebro.plot()  # Plot the backtest results
    elif mode == 'live':
        cerebro.addstrategy(SimpleStrategy)  # Add the trading strategy to the backtesting engine
        cerebro.broker.set_cash(1000)  # Set your initial capital to 1000 USDT
        cerebro.broker.set_coc(True)  # Close on close (no intra-candle operations)
        cerebro.broker.setcommission(commission=0.001)  # Set the Binance trading fee to 0.1% (0.001 as a fraction)

        broker = cerebro.getbroker()
        broker.setcommission(commission=0.001)  # Set the Binance trading fee

        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        # Print the starting portfolio value before running the live trading

        cerebro.run()  # Run the live trading
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
        # Print the final portfolio value after the live trading
