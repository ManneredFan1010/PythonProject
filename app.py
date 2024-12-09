from flask import Flask, render_template, request, url_for
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import os

# Set non-GUI backend for Matplotlib
plt.switch_backend('Agg')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    stock = None
    current_price = None
    simulation_image = None
    monte_carlo_prediction = None
    error = None

    if request.method == 'POST':
        stock = request.form.get('stock').upper()  # Get stock symbol and convert to uppercase
        try:
            ticker = yf.Ticker(stock)
            
            # Fetch live stock data
            live_data = ticker.history(period='1d')
            if live_data.empty:
                error = f'No data found for symbol: {stock}'
            else:
                current_price = live_data['Close'].iloc[-1]

                # Get historical data for Monte Carlo simulation
                historical_data = ticker.history(period='1y')
                daily_returns = historical_data['Close'].pct_change().dropna()

                # Monte Carlo Simulation
                num_simulations = 100  # Number of simulation runs
                num_days = 252  # Number of trading days in a year
                last_close = historical_data['Close'].iloc[-1]
                simulation_results = []

                for _ in range(num_simulations):
                    simulated_prices = [last_close]
                    for _ in range(num_days):
                        simulated_price = simulated_prices[-1] * (1 + np.random.choice(daily_returns))
                        simulated_prices.append(simulated_price)
                    simulation_results.append(simulated_prices)

                # Create Monte Carlo Graph
                plt.figure(figsize=(10, 6))
                for simulation in simulation_results:
                    plt.plot(simulation, color='lightblue', alpha=0.3)
                plt.title(f'Monte Carlo Simulation for {stock}')
                plt.xlabel('Days')
                plt.ylabel('Price')
                plt.grid()

                # Save the graph as an image
                graph_path = os.path.join('static', 'monte_carlo_simulation.png')
                plt.savefig(graph_path)
                plt.close()

                simulation_image = url_for('static', filename='monte_carlo_simulation.png')

                # Monte Carlo prediction
                monte_carlo_prediction = np.mean([result[-1] for result in simulation_results])

        except Exception as e:
            error = f'Error retrieving data: {e}'
    
    return render_template('index.html', stock=stock, current_price=current_price, monte_carlo_prediction=monte_carlo_prediction, simulation_image=simulation_image, error=error)

if __name__ == '__main__':
    app.run(debug=True)
