from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

API_KEY = 'OP33PL97YI3IQKBO'

# Sample users for login
users = {
    'Neel': '123',
    'Abhi': '1234',
    'Meet': '12345',
    'Mansi': '123456'
}

# Function to get the current stock price
def get_stock_price(ticker):
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={API_KEY}'
    response = requests.get(url).json()
    if "Global Quote" in response:
        return response["Global Quote"]["05. price"]
    return None

# Function to get historical stock data (daily prices)
def get_historical_data(ticker):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={API_KEY}&outputsize=compact'
    response = requests.get(url).json()
    if "Time Series (Daily)" in response:
        return response["Time Series (Daily)"]
    else:
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['user'] = username
            session['watchlist'] = []
            session['alerts'] = [] 
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('watchlist', None)
    session.pop('alerts', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    watchlist = session.get('watchlist', [])
    stock_data = {ticker: get_stock_price(ticker) for ticker in watchlist}

    alerts = session.get('alerts', [])
    triggered_alerts = []

    # Checking if the price has reached the alert threshold
    for alert in alerts:
        current_price = get_stock_price(alert['ticker'])
        if current_price and float(current_price) >= alert['price']:
            triggered_alerts.append(alert)

    if triggered_alerts:
        for alert in triggered_alerts:
            flash(f"Price alert triggered for {alert['ticker']} at ${alert['price']}!", "info")
        session['alerts'] = [alert for alert in alerts if alert not in triggered_alerts]

    return render_template('index.html', stock_data=stock_data, alerts=session.get('alerts', []))

@app.route('/add', methods=['POST'])
def add_company():
    if 'user' not in session:
        return redirect(url_for('login'))

    ticker = request.form['ticker'].upper()
    watchlist = session.get('watchlist', [])
    if ticker not in watchlist:
        watchlist.append(ticker)
        session['watchlist'] = watchlist
        flash(f"{ticker} added to your watchlist!", "success")
    else:
        flash(f"{ticker} is already in your watchlist.", "error")
    return redirect(url_for('index'))

@app.route('/remove/<ticker>')
def remove_company(ticker):
    if 'user' not in session:
        return redirect(url_for('login'))

    watchlist = session.get('watchlist', [])
    if ticker in watchlist:
        watchlist.remove(ticker)
        session['watchlist'] = watchlist
        flash(f"{ticker} removed from your watchlist!", "success")
    return redirect(url_for('index'))

@app.route('/set_alert', methods=['POST'])
def set_alert():
    if 'user' not in session:
        return redirect(url_for('login'))

    ticker = request.form['ticker'].upper()
    alert_price = float(request.form['alert_price'])
    
    alerts = session.get('alerts', [])
    alerts.append({'ticker': ticker, 'price': alert_price})
    session['alerts'] = alerts
    flash(f"Price alert set for {ticker} at ${alert_price}!", "success")
    
    return redirect(url_for('index'))

@app.route('/remove_alert/<ticker>')
def remove_alert(ticker):
    if 'user' not in session:
        return redirect(url_for('login'))

    alerts = session.get('alerts', [])
    alerts = [alert for alert in alerts if alert['ticker'] != ticker]
    session['alerts'] = alerts
    flash(f"Price alert removed for {ticker}", "success")
    return redirect(url_for('index'))

# Route to display historical data for a stock
@app.route('/historical/<ticker>')
def historical(ticker):
    historical_data = get_historical_data(ticker)
    
    if historical_data or True:
        # Get the most recent 30 dates and closing prices for the chart
        historical_data = {'2024-10-23': {'1. open': '188.8500', '2. high': '189.1600', '3. low': '183.6900', '4. close': '184.7100', '5. volume': '31937089'}, '2024-10-22': {'1. open': '188.3500', '2. high': '191.5201', '3. low': '186.9750', '4. close': '189.7000', '5. volume': '29650593'}, '2024-10-21': {'1. open': '188.0500', '2. high': '189.4600', '3. low': '186.4000', '4. close': '189.0700', '5. volume': '24639393'}, '2024-10-18': {'1. open': '187.1500', '2. high': '190.7400', '3. low': '186.2800', '4. close': '188.9900', '5. volume': '37417670'}, '2024-10-17': {'1. open': '188.2200', '2. high': '188.9400', '3. low': '186.0000', '4. close': '187.5300', '5. volume': '25039414'}, '2024-10-16': {'1. open': '187.0500', '2. high': '187.7800', '3. low': '185.6100', '4. close': '186.8900', '5. volume': '23456812'}, '2024-10-15': {'1. open': '187.6300', '2. high': '188.4100', '3. low': '184.5800', '4. close': '187.6900', '5. volume': '32178925'}, '2024-10-14': {'1. open': '189.7800', '2. high': '189.8300', '3. low': '187.3600', '4. close': '187.5400', '5. volume': '22614407'}, '2024-10-11': {'1. open': '186.6300', '2. high': '189.9284', '3. low': '186.3000', '4. close': '188.8200', '5. volume': '25751557'}, '2024-10-10': {'1. open': '187.1300', '2. high': '188.1340', '3. low': '185.8300', '4. close': '186.6500', '5. volume': '27785043'}, '2024-10-09': {'1. open': '182.8200', '2. high': '185.8450', '3. low': '182.0500', '4. close': '185.1700', '5. volume': '26343117'}, '2024-10-08': {'1. open': '181.9150', '2. high': '183.0900', '3. low': '180.9200', '4. close': '182.7200', '5. volume': '26372086'}, '2024-10-07': {'1. open': '182.9500', '2. high': '183.6000', '3. low': '180.2500', '4. close': '180.8000', '5. volume': '42364201'}, '2024-10-04': {'1. open': '185.7500', '2. high': '187.6000', '3. low': '183.6000', '4. close': '186.5100', '5. volume': '41079011'}, '2024-10-03': {'1. open': '183.0450', '2. high': '183.4400', '3. low': '180.8750', '4. close': 
'181.9600', '5. volume': '30204302'}, '2024-10-02': {'1. open': '184.4400', '2. high': '186.6000', '3. low': '184.0400', '4. close': '184.7600', '5. volume': '23704056'}, '2024-10-01': {'1. open': '184.9000', '2. high': '186.1900', '3. low': '183.4519', '4. close': '185.1300', '5. volume': '36044906'}, '2024-09-30': {'1. open': '187.1400', '2. high': '188.4900', '3. low': '184.6500', '4. close': '186.3300', '5. volume': '41680400'}, '2024-09-27': {'1. open': '190.6800', '2. high': '190.9000', '3. low': '187.3400', '4. close': '187.9700', '5. volume': '36002316'}, '2024-09-26': {'1. open': '194.3100', '2. high': '194.5300', '3. low': '189.5400', '4. close': '191.1600', '5. volume': '36334854'}, '2024-09-25': {'1. open': '193.7500', '2. high': '193.9498', '3. low': '192.1600', '4. close': '192.5300', '5. volume': '26391144'}, '2024-09-24': {'1. open': '194.2700', '2. high': '195.3700', '3. low': '190.1300', '4. close': '193.9600', '5. volume': '43478926'}, '2024-09-23': {'1. open': '191.6400', '2. high': '194.4500', '3. low': '190.5700', '4. close': '193.8800', '5. volume': '36993111'}, '2024-09-20': {'1. open': '190.2300', '2. high': '191.8400', '3. low': '187.4100', '4. close': '191.6000', '5. volume': '100378553'}, '2024-09-19': {'1. open': '190.0400', '2. high': '190.9900', '3. low': '188.4700', '4. close': '189.8700', '5. volume': '39543168'}, '2024-09-18': {'1. open': '186.4500', '2. high': '188.8000', '3. low': '185.0600', '4. close': '186.4300', '5. volume': '34448130'}, '2024-09-17': {'1. open': '186.8500', '2. high': '189.4500', '3. low': '186.1400', '4. close': '186.8800', '5. volume': '26091682'}, '2024-09-16': {'1. open': '185.2900', '2. high': '185.8100', '3. low': '183.3600', '4. close': '184.8900', '5. volume': '26065485'}, '2024-09-13': {'1. open': '187.0000', '2. high': '188.5000', '3. low': '185.9100', '4. close': '186.4900', '5. volume': '26495351'}, '2024-09-12': {'1. open': '184.8000', '2. high': '187.4100', '3. low': '183.5400', '4. close': '187.0000', '5. volume': '33622483'}, '2024-09-11': {'1. open': '180.0950', '2. high': '184.9900', '3. low': '175.7300', '4. close': '184.5200', '5. volume': '42564698'}, '2024-09-10': {'1. open': '177.4900', '2. high': '180.5000', '3. low': '176.7900', '4. close': '179.5500', '5. volume': '36233796'}, '2024-09-09': 
{'1. open': '174.5300', '2. high': '175.8500', '3. low': '173.5100', '4. close': '175.4000', '5. volume': '29037362'}, '2024-09-06': {'1. open': '177.2400', '2. high': '178.3800', '3. low': '171.1600', '4. close': '171.3900', '5. volume': '41466537'}, '2024-09-05': {'1. open': '175.0000', '2. high': '179.8750', '3. low': '174.9950', '4. close': '177.8900', '5. volume': '40170526'}, '2024-09-04': {'1. open': '174.4800', '2. high': '175.9800', '3. low': '172.5400', '4. close': '173.3300', '5. volume': '29682478'}, '2024-09-03': {'1. open': '177.5500', '2. high': '178.2600', '3. low': '175.2600', '4. close': '176.2500', '5. volume': '37817511'}, '2024-08-30': {'1. open': '172.7800', '2. high': '178.9000', 
'3. low': '172.6000', '4. close': '178.5000', '5. volume': '43429355'}, '2024-08-29': {'1. open': '173.2200', '2. high': '174.2900', '3. low': '170.8100', '4. close': '172.1200', '5. volume': '26407815'}, '2024-08-28': {'1. open': '173.6900', '2. high': '173.6900', '3. low': '168.9200', '4. close': '170.8000', '5. volume': '29045025'}, '2024-08-27': {'1. open': '174.1500', '2. high': '174.8900', '3. low': '172.2500', '4. close': '173.1200', '5. volume': '29841979'}, '2024-08-26': {'1. open': '176.7000', '2. high': '177.4682', '3. low': '174.3000', '4. close': '175.5000', '5. volume': '22366236'}, '2024-08-23': {'1. open': '177.3400', '2. high': '178.9699', '3. low': '175.2400', '4. close': '177.0400', '5. volume': '29150091'}, '2024-08-22': {'1. open': '181.3800', '2. high': '181.4700', '3. low': '175.6800', '4. close': '176.1300', '5. volume': '32047482'}, '2024-08-21': {'1. open': '179.9200', '2. high': '182.3850', '3. low': '178.8937', '4. close': '180.1100', '5. volume': '35599120'}, '2024-08-20': {'1. open': '177.9200', '2. high': '179.0100','3. low': '177.4308', '4. close': '178.8800', '5. volume': '26255204'}, '2024-08-19': {'1. open': '177.6400', '2. high': '178.3000', '3. low': '176.1600', '4. close': '178.2200', '5. volume': '31129807'}, '2024-08-16': {'1. open': '177.0400', '2. high': '178.3400', '3. low': '176.2601', '4. close': '177.0600', '5. volume': '31489175'}, '2024-08-15': {'1. open': '174.8600', '2. high': '177.9100', '3. low': '173.9900', '4. close': '177.5900', '5. volume': '51698513'}, '2024-08-14': {'1. open': '172.1100', '2. high': '172.2800', '3. low': '168.8600', '4. close': '170.1000', '5. volume': '28843804'}, '2024-08-13': {'1. open': '167.8100', '2. high': '171.0400', '3. low': '167.1000', '4. close': '170.2300', '5. volume': '39237915'}, '2024-08-12': {'1. open': '168.1400', '2. high': '168.5500', '3. low': '166.1101', '4. close': '166.8000', '5. volume': '30072788'}, '2024-08-09': {'1. open': '166.4000', '2. high': '168.5500', '3. low': '165.8500', '4. close': '166.9400', '5. volume': '36401049'}, '2024-08-08': {'1. open': '165.1650', '2. high': '166.6899', '3. low': '162.5500', '4. close': '165.8000', '5. volume': '44616206'}, '2024-08-07': {'1. open': '166.5500', '2. high': '167.5800', '3. low': '161.4300', '4. close': '162.7700', '5. volume': '48408240'}, '2024-08-06': {'1. open': '161.7100', '2. high': '165.0800', '3. low': '158.5404', '4. close': '161.9300', '5. volume': '59950830'}, '2024-08-05': {'1. open': 
'154.2100', '2. high': '162.9600', '3. low': '151.6100', '4. close': '161.0200', '5. volume': '83149437'}, '2024-08-02': {'1. open': '166.7500', '2. high': '168.7700', '3. low': 
'160.5500', '4. close': '167.9000', '5. volume': '141448365'}, '2024-08-01': {'1. open': '189.2850', '2. high': '190.6000', '3. low': '181.8700', '4. close': '184.0700', '5. volume': '70435635'}, '2024-07-31': {'1. open': '185.0500', '2. high': '187.9400', '3. low': '184.4600', '4. close': '186.9800', '5. volume': '41667326'}, '2024-07-30': {'1. open': '184.7200', '2. high': '185.8600', '3. low': '179.3800', '4. close': '181.7100', '5. volume': '39508574'}, '2024-07-29': {'1. open': '183.8400', '2. high': '184.7500', '3. low': '182.3800', '4. close': '183.2000', '5. volume': '33270123'}, '2024-07-26': {'1. open': '180.3900', '2. high': '183.1900', '3. low': '180.2400', '4. close': '182.5000', '5. volume': '29505964'}, '2024-07-25': {'1. open': '182.9100', '2. high': '183.8958', '3. low': '176.8000', '4. close': '179.8500', '5. volume': '44464163'}, '2024-07-24': {'1. open': '183.2000', '2. high': '185.4500', '3. low': '180.4100', '4. close': '180.8300', '5. volume': '41532360'}, '2024-07-23': {'1. open': '184.1000', '2. high': '189.3900', '3. low': '183.5600', '4. close': '186.4100', '5. volume': '47537670'}, '2024-07-22': {'1. open': '185.0000', '2. high': '185.0600', '3. low': '182.4800', '4. close': '182.5500', '5. volume': '39931923'}, '2024-07-19': {'1. open': '181.1400', '2. high': '184.9300', '3. low': '180.1100', '4. close': '183.1300', '5. volume': '43081829'}, '2024-07-18': {'1. open': '189.5900', '2. high': '189.6800', '3. low': '181.4480', '4. close': '183.7500', '5. volume': '51043626'}, '2024-07-17': {'1. open': '191.3500', '2. high': '191.5800', '3. low': '185.9900', '4. close': '187.9300', '5. volume': '48076139'}, '2024-07-16': {'1. open': '195.5900', '2. high': '196.6200', '3. low': '192.2400', '4. close': '193.0200', '5. volume': '33994714'}, '2024-07-15': {'1. open': '194.5600', '2. high': '196.1900', '3. low': '190.8300', '4. close': '192.7200', '5. volume': '40683227'}, '2024-07-12': {'1. open': '194.8000', '2. high': '196.4700', '3. low': '193.8301', '4. close': '194.4900', '5. volume': '30598525'}, '2024-07-11': {'1. open': '200.0900', '2. high': '200.2699', '3. low': '192.8600', '4. close': '195.0500', '5. volume': '44565041'}, '2024-07-10': {'1. open': '199.9950', '2. high': '200.1100', '3. low': '197.6900', '4. close': '199.7900', '5. volume': '32883753'}, '2024-07-09': {'1. open': '199.4000', '2. high': '200.5700', '3. low': '199.0450', '4. close': '199.3400', '5. volume': '32756736'}, '2024-07-08': {'1. open': '200.0400', '2. high': '201.2000', '3. low': '197.9600', '4. close': '199.2900', '5. volume': '34767261'}, '2024-07-05': {'1. open': '198.6500', '2. high': '200.5500', '3. low': '198.1700', '4. close': '200.0000', '5. volume': '39858885'}, '2024-07-03': {'1. open': '199.9400', '2. high': '200.0290', '3. low': '196.7601', '4. close': '197.5900', '5. volume': '31597926'}, '2024-07-02': {'1. open': '197.2800', '2. high': '200.4300', '3. low': '195.9300', '4. close': '200.0000', '5. volume': '45600013'}, '2024-07-01': {'1. open': '193.4900', '2. high': '198.2957', '3. low': '192.8200', '4. close': '197.2000', '5. volume': '41192011'}, '2024-06-28': {'1. open': '197.7300', '2. high': '198.8500', '3. low': '192.5000', '4. close': '193.2500', '5. volume': '76930192'}, '2024-06-27': {'1. open': '195.0050', '2. high': '199.8400', '3. low': '194.2000', '4. close': '197.8500', '5. volume': '74397491'}, '2024-06-26': {'1. open': '186.9200', '2. high': '194.8000', '3. low': '186.2600', '4. close': '193.6100', '5. volume': '65103893'}, '2024-06-25': {'1. open': '186.8100', '2. high': '188.8400', '3. low': '185.4200', '4. close': '186.3400', '5. volume': '45898475'}, '2024-06-24': {'1. open': '189.3300', '2. high': '191.0000', '3. low': '185.3300', '4. close': '185.5700', '5. volume': '50610379'}, '2024-06-21': {'1. open': '187.8000', '2. high': '189.2750', '3. low': '185.8600', '4. close': '189.0800', '5. volume': '72931754'}, '2024-06-20': {'1. open': '182.9100', '2. high': '186.5100', '3. low': '182.7200', '4. close': '186.1000', '5. volume': '44726779'}, '2024-06-18': {'1. open': '183.7350', '2. high': '184.2900', '3. low': '181.4300', '4. close': '182.8100', '5. volume': '36659157'}, '2024-06-17': {'1. open': '182.5200', '2. high': '185.0000', '3. low': '181.2200', '4. close': '184.0600', '5. volume': '35601907'}, '2024-06-14': {'1. open': '183.0800', '2. high': '183.7200', '3. low': '182.2300', '4. close': '183.6600', '5. volume': '25456410'}, '2024-06-13': {'1. open': '186.0900', '2. high': '187.6700', '3. low': '182.6660', '4. close': '183.8300', '5. volume': '39721545'}, '2024-06-12': {'1. open': '188.0150', '2. high': '188.3500', '3. low': '185.4300', '4. close': '186.8900', '5. volume': '33984216'}, '2024-06-11': {'1. open': '187.0600', '2. high': '187.7700', '3. low': '184.5373', '4. close': '187.2300', '5. volume': '27265108'}, '2024-06-10': {'1. open': '184.0700', '2. high': '187.2300', '3. low': '183.7900', '4. close': '187.0600', '5. volume': '34494498'}, 
'2024-06-07': {'1. open': '184.9000', '2. high': '186.2888', '3. low': '183.3600', '4. close': '184.3000', '5. volume': '28021473'}, '2024-06-06': {'1. open': '181.7450', '2. high': '185.0000', '3. low': '181.4900', '4. close': '185.0000', '5. volume': '31371151'}, '2024-06-05': {'1. open': '180.1000', '2. high': '181.5000', '3. low': '178.7500', '4. close': '181.2800', '5. volume': '32116394'}, '2024-06-04': {'1. open': '177.6400', '2. high': '179.8200', '3. low': '176.4400', '4. close': '179.3400', '5. volume': '27198388'}, '2024-06-03': {'1. open': '177.7000', '2. high': '178.7000', '3. low': '175.9200', '4. close': '178.3400', '5. volume': '30786640'}}
        dates = list(historical_data.keys())[:30]  # Fetch 30 recent dates
        prices = [float(historical_data[date]["4. close"]) for date in dates]

        # Reverse the data so that the oldest date is first
        dates.reverse()
        prices.reverse()

        print(dates, prices)

        historical_data_list = []
        for date in dates:
            historical_data_list.append({
                'date': date,
                'open': float(historical_data[date]["1. open"]),
                'high': float(historical_data[date]["2. high"]),
                'low': float(historical_data[date]["3. low"]),
                'close': float(historical_data[date]["4. close"]),
                'volume': historical_data[date]["5. volume"]
            })

        historical_data_list.reverse()

        return render_template('historical.html', ticker=ticker, historical_data=historical_data_list)

    else:
        flash(f"Could not fetch historical data for {ticker}.", "error")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
