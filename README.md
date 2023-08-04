# Python Trading Bot with Backtest (Binance API) by Chat GPT

### CODE EXPLAINED:

Let's go through each section of the code and its purpose:

1. Importing Libraries: 
   Import necessary libraries for the code to work: backtrader for backtesting, configparser for reading configuration files, rarfile for extracting RAR archives, getpass for secure password input, os for file operations, and Client from binance.client for Binance API interaction.

```python
import backtrader as bt
import configparser
import rarfile
import getpass
import os
from binance.client import Client
```
2. Defining extract_config Function

Define a function extract_config to extract the content of the config.ini file from a password-protected RAR archive.
This function takes two parameters: rar_path (path to the RAR archive) and password (password for the archive).
It uses the rarfile library to open the RAR archive, set the password, and read the content of config.ini.
The extracted content is returned as a string.

```python
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
```
3. Entering RAR Password and Extracting API Keys


Prompt the user to enter the password for the RAR archive containing the config.ini file using getpass.getpass.
Call the extract_config function to extract the content of config.ini using the provided password.
Parse the API keys (Binance API key and secret) from the extracted config.ini content using the configparser library.

```python
rar_password = getpass.getpass("Enter password for the RAR archive: ")

config_content = extract_config('protected_config.rar', rar_password)

config = configparser.ConfigParser()
config.read_string(config_content)

API_KEY = config.get('binance', 'api_key')
API_SECRET = config.get('binance', 'api_secret')
```

4. Defining SimpleStrategy Class

```python
Define a trading strategy class SimpleStrategy that inherits from bt.Strategy.
This class implements a simple trading strategy based on a Simple Moving Average (SMA) crossover.
The strategy uses the SMA indicator to make trading decisions.
The params attribute allows specifying parameters for the strategy, such as the SMA period.

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
```

5. Backtesting and Live Trading Explanation:

The code is enclosed in an if __name__ == '__main__': block. This ensures that the contained code is executed only when the script is run directly, not when imported as a module.

The user is prompted to choose a mode (backtest or live) using the input function. The chosen mode is converted to lowercase and stored in the mode variable.

An instance of the Cerebro class, named cerebro, is created. Cerebro is the backtesting and optimization engine in backtrader.

If the chosen mode is 'backtest':

Historical data from Binance is fetched using the Client class, and daily klines (candlestick data) for the symbol 'BTCUSDT' are obtained.
The fetched data is converted into a PandasData feed and added to the backtesting engine using cerebro.adddata(data).
The SimpleStrategy class is added as the trading strategy to the backtesting engine.
Initial parameters for the broker, such as cash, closing operation mode, and commission, are set.
The starting portfolio value is printed, the backtest is executed using cerebro.run(), and the final portfolio value is printed.
The backtest results are plotted using cerebro.plot().
The extracted config.ini file is removed using os.remove() to ensure security.
If the chosen mode is 'live':

The SimpleStrategy class is added as the trading strategy to the backtesting engine.
Initial parameters for the broker are set similarly to the backtesting mode.
The starting portfolio value is printed, and the live trading is executed using cerebro.run().
The final portfolio value after live trading is printed.
The sections provide a choice between backtesting and live trading modes, configure the backtesting engine, execute the chosen mode, and display results.

   
```python
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

        # Remove the extracted config.ini file
        os.remove('config.ini')

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
```

### SECURITY PRECAUTIONS EXPLAINED:

Keep API Keys Private: Never share your API keys or sensitive information with anyone. Keep them secret to prevent unauthorized access to your account.

Secure Password Entry: Ensure you enter the RAR archive password in a trusted and secure environment, free from keyloggers or malware.

Secure API Key Storage: Store your API keys and password-protected RAR archive in a secure location on your local machine, accessible only to you.

Regularly Update Passwords: Periodically update your passwords, both for your Binance account and the RAR archive.

Two-Factor Authentication (2FA): Enable 2FA for your Binance account to add an extra layer of security.

Secure Execution Environment: Run the code on a trusted and secure computer or virtual environment.

Code Review: Review the code for any vulnerabilities before running it, and only use scripts from trusted sources.

Limit API Permissions: When creating API keys on Binance, limit their permissions to only what your script requires (e.g., trading and accessing market data).

### INSTALLATION EXPLAINED:

Install Python: If you haven't already, download and install Python from the official website (https://www.python.org/downloads/). Choose the appropriate version for your operating system.

Install Required Libraries: Open a terminal or command prompt and install the required libraries by running the following commands:

pip install backtrader
pip install python-binance

Create Config File: Create a protected_config.rar file containing your config.ini with your Binance API keys. Make sure it's password-protected.

Place Files: Place the protected_config.rar file and the Python script (provided above) in the same directory.

Run the Script: Open a terminal or command prompt, navigate to the directory containing the script, and run the script using the command:

python script_name.py

Choose Mode: The script will prompt you to choose a mode: backtest or live. Select the desired mode.

Follow Instructions: Follow the on-screen instructions to provide the RAR archive password and see the backtesting or live trading results.

Please ensure you understand the code, the security precautions, and the steps provided before proceeding. Always prioritize security and exercise caution when handling sensitive information.




