import random
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


class Order:
    def __init__(self, order_id, price, quantity, side):
        self.order_id = order_id
        self.price = price
        self.quantity = quantity
        self.side = side

    def __lt__(self, other):
        if self.side == 'buy':
            return self.price > other.price
        else:
            return self.price < other.price


class OrderBook:
    def __init__(self, security_price):
        self.order_id = 0
        self.buy_orders = []
        self.sell_orders = []
        self.security_price = security_price
        self.trades = pd.DataFrame(columns=['Order ID', 'Price'])

    def place_order(self, price, quantity, side):
        if quantity < 1:
            print("Invalid quantity. Minimum quantity should be 1.")
            return

        order = Order(self.order_id, price, quantity, side)
        self.order_id += 1

        if side == 'buy':
            self.buy_orders.append(order)
            # Sort buy orders in descending order
            self.buy_orders.sort(reverse=True)
        else:
            self.sell_orders.append(order)
        self.sell_orders.sort()  # Sort sell orders in ascending order

        self.match_orders(order)

    def match_orders(self, new_order):
        if new_order.side == 'buy':
            opposite_orders = self.sell_orders
        else:
            opposite_orders = self.buy_orders

        while opposite_orders and new_order.quantity > 0:
            opposite_order = opposite_orders[0]
            if (new_order.side == 'buy' and opposite_order.price <= new_order.price) or \
                    (new_order.side == 'sell' and opposite_order.price >= new_order.price):
                traded_quantity = min(new_order.quantity,
                                      opposite_order.quantity)
                opposite_order.quantity -= traded_quantity
                new_order.quantity -= traded_quantity

                # Calculate weighted average price if total quantity is non-zero
                total_quantity = traded_quantity + opposite_order.quantity
                if total_quantity > 0:
                    total_quantity += self.security_price * \
                        (traded_quantity + opposite_order.quantity)
                    self.security_price = total_quantity / \
                        (traded_quantity + opposite_order.quantity)

                # Add the trade to the dataframe
                self.trades = self.trades.append({'Order ID': new_order.order_id, 'Price': opposite_order.price},
                                                 ignore_index=True)

                # Remove the filled order from the opposite order list if fully traded
                if opposite_order.quantity == 0:
                    opposite_orders.pop(0)

                # If the new order is fully traded, exit the loop
                if new_order.quantity == 0:
                    break

            else:
                break

    def cancel_order(self, order_id, side):
        if side == 'buy':
            orders = self.buy_orders
        else:
            orders = self.sell_orders

        for order in orders:
            if order.order_id == order_id:
                orders.remove(order)
                break

    def print_order_book(self):
        print("Buy Orders:")
        for order in self.buy_orders:
            print(
                f"Order ID: {order.order_id}, Price: {order.price}, Quantity: {order.quantity}")

        print("Sell Orders:")
        for order in self.sell_orders:
            print(
                f"Order ID: {order.order_id}, Price: {order.price}, Quantity: {order.quantity}")


def run_simulation(num_orders):
    security_price = 100  # Initial price of the security
    order_book = OrderBook(security_price)

    for _ in range(num_orders):
        # Generate a random order
        generated_price = random.randint(90, 110)
        quantity = random.randint(1, 10)
        side = random.choice(['buy', 'sell'])
        order_book.place_order(generated_price, quantity, side)

    # Print the final security price and the order book
    print("Final Security Price:", order_book.security_price)
    order_book.print_order_book()

    # Print the trades dataframe
    print("\nTrades:")
    print(order_book.trades)

    return order_book


# Run the simulation with 1000 orders
simulation_result = run_simulation(100)
