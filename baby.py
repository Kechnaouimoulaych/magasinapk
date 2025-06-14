from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.checkbox import CheckBox
import sqlite3
import datetime
import os

# --- Custom Widgets (No changes here) ---

class ModernCard(BoxLayout):
    def __init__(self, title="", content="", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(120)
        
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1) 
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        self.title_label = Label(
            text=title,
            font_size=dp(16),
            bold=True,
            color=(0.2, 0.2, 0.2, 1), 
            size_hint_y=0.4,
            text_size=(self.width - dp(30), None),
            halign='left',
            valign='top'
        )
        self.add_widget(self.title_label)
        
        self.content_label = Label(
            text=content,
            font_size=dp(14),
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=0.6,
            text_size=(self.width - dp(30), None),
            halign='left',
            valign='top'
        )
        self.add_widget(self.content_label)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        # Update text_size for wrapping
        self.title_label.text_size = (self.width - dp(30), None)
        self.content_label.text_size = (self.width - dp(30), None)


class ModernButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.2, 0.6, 0.86, 1) 
        self.color = (1, 1, 1, 1)
        self.font_size = dp(14)
        self.size_hint_y = None
        self.height = dp(45)
        self.background_normal = ''

class ModernTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.9, 0.9, 0.9, 1)
        self.foreground_color = (0.1, 0.1, 0.1, 1)
        self.size_hint_y = None
        self.height = dp(40)
        self.multiline = False

# --- DATABASE MANAGER (No changes here) ---
class DatabaseManager:
    def __init__(self, db_name='store.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.create_tables()
        self.init_sample_data()

    def _execute(self, query, params=()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor

    def _rows_to_dicts(self, cursor, rows):
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def create_tables(self):
        self._execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT, price REAL NOT NULL,
                stock INTEGER NOT NULL, supplier TEXT, size TEXT, age_range TEXT, color TEXT, material TEXT, condition TEXT)''')
        self._execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT, phone TEXT,
                total_purchases REAL DEFAULT 0, baby_name TEXT, baby_age TEXT)''')
        self._execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, customer_name TEXT, product_name TEXT,
                quantity INTEGER, total REAL, size TEXT)''')

    def init_sample_data(self):
        cursor = self._execute('SELECT COUNT(*) FROM products')
        if cursor.fetchone()[0] == 0:
            products = [
                ("Baby Onesie Set", "Bodysuits", 24.99, 17, "Baby Comfort Co", "0-3M", "0-3M", "Pink", "Cotton", "New"),
                ("Infant Sleep Gown", "Sleepwear", 18.99, 11, "Sleepy Baby", "3-6M", "3-6M", "Blue", "Organic Cotton", "New"),
                ("Newborn Romper", "Outerwear", 32.99, 12, "Little Angels", "Newborn", "Newborn", "Yellow", "Bamboo", "Gently Used"),
                ("Baby Footie Pajamas", "Sleepwear", 22.99, 4, "Cozy Dreams", "6-9M", "6-9M", "White", "Cotton Blend", "New"),
            ]
            self._execute('BEGIN TRANSACTION')
            for p in products:
                self._execute('INSERT INTO products (name, category, price, stock, supplier, size, age_range, color, material, condition) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', p)
            self._execute('COMMIT')

            customers = [
                ("Emma Johnson", "emma.j@email.com", "123-456-7890", 39.99, "Lily", "3 months"),
                ("Sarah Williams", "sarah.w@email.com", "098-765-4321", 99.97, "Max", "8 months"),
            ]
            self._execute('BEGIN TRANSACTION')
            for c in customers:
                self._execute('INSERT INTO customers (name, email, phone, total_purchases, baby_name, baby_age) VALUES (?, ?, ?, ?, ?, ?)', c)
            self._execute('COMMIT')
            
            all_products = self.get_all_products()
            all_customers = self.get_all_customers()
            emma = next(c for c in all_customers if c['name'] == "Emma Johnson")
            sarah = next(c for c in all_customers if c['name'] == "Sarah Williams")
            onesie = next(p for p in all_products if p['name'] == "Baby Onesie Set")
            gown = next(p for p in all_products if p['name'] == "Infant Sleep Gown")

            sale1 = {'date': "2024-06-10", 'customer': emma['name'], 'product': onesie['name'], 'quantity': 2, 'total': 2 * onesie['price'], 'size': onesie['size']}
            self.add_sale(sale1, onesie['id'], emma['id'])
            sale2 = {'date': "2024-06-12", 'customer': sarah['name'], 'product': gown['name'], 'quantity': 3, 'total': 3 * gown['price'], 'size': gown['size']}
            self.add_sale(sale2, gown['id'], sarah['id'])

    def get_all_products(self):
        cursor = self._execute('SELECT * FROM products ORDER BY name')
        return self._rows_to_dicts(cursor, cursor.fetchall())
    
    def add_product(self, data):
        self._execute('INSERT INTO products (name, category, price, stock, condition, age_range, size, color, material, supplier) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (data['name'], data['category'], data['price'], data['stock'], data['condition'], data['age_range'], data['size'], data['color'], data['material'], data['supplier']))

    def update_product(self, data):
        self._execute('UPDATE products SET name=?, category=?, price=?, stock=?, condition=?, age_range=?, size=?, color=?, material=?, supplier=? WHERE id=?',
                     (data['name'], data['category'], data['price'], data['stock'], data['condition'], data['age_range'], data['size'], data['color'], data['material'], data['supplier'], data['id']))

    def delete_product(self, product_id):
        self._execute('DELETE FROM products WHERE id=?', (product_id,))

    def get_all_customers(self):
        cursor = self._execute('SELECT * FROM customers ORDER BY name')
        return self._rows_to_dicts(cursor, cursor.fetchall())

    def add_customer(self, data):
        self._execute('INSERT INTO customers (name, email, phone, baby_name, baby_age, total_purchases) VALUES (?, ?, ?, ?, ?, 0)',
                     (data['name'], data['email'], data['phone'], data['baby_name'], data['baby_age']))

    def get_all_sales(self):
        cursor = self._execute('SELECT * FROM sales ORDER BY id DESC')
        return self._rows_to_dicts(cursor, cursor.fetchall())

    def add_sale(self, sale_data, product_id, customer_id):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO sales (date, customer_name, product_name, quantity, total, size) VALUES (?, ?, ?, ?, ?, ?)',
                               (sale_data['date'], sale_data['customer'], sale_data['product'], sale_data['quantity'], sale_data['total'], sale_data['size']))
                cursor.execute('UPDATE products SET stock = stock - ? WHERE id = ?', (sale_data['quantity'], product_id))
                cursor.execute('UPDATE customers SET total_purchases = total_purchases + ? WHERE id = ?', (sale_data['total'], customer_id))
        except sqlite3.Error as e:
            print(f"Database transaction failed: {e}")

# (### NEW ###) --- RESPONSIVE BASE CLASS ---
class ResponsiveScreen(Screen):
    breakpoint = dp(600)  # Width threshold to switch between mobile/desktop

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._is_built = False
        Window.bind(on_resize=self.on_window_resize)

    def on_enter(self, *args):
        if not self._is_built:
            self.build_ui()
            self._is_built = True
        self.update_layout() # Call on enter to set initial layout
        self.refresh_data()  # Method to be implemented by child screens

    def on_window_resize(self, window, width, height):
        self.update_layout()

    def build_ui(self):
        """To be implemented by subclasses to create widgets."""
        pass

    def update_layout(self):
        """To be implemented by subclasses to adjust layout based on size."""
        pass
    
    def refresh_data(self):
        """To be implemented by subclasses to reload data from DB."""
        pass

# --- Navigation Widgets ---

class NavigationCard(ButtonBehavior, BoxLayout):
    def __init__(self, title, screen_name, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(15)
        # FLEXIBLE: Use size_hint_x to fill grid width
        self.size_hint = (1, None) 
        self.height = dp(150)
        self.screen_name = screen_name
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.add_widget(Widget()) 
        title_label = Label(text=title, font_size=dp(24), bold=True, color=(0.1, 0.3, 0.5, 1))
        self.add_widget(title_label)
        self.add_widget(Widget())
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    def on_press(self):
        App.get_running_app().root.current = self.screen_name

class NavigationScreen(ResponsiveScreen):
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        header = Label(text='Store Management System', font_size=dp(32), bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(80))
        main_layout.add_widget(header)

        # FLEXIBLE: Grid layout will now be adjusted dynamically
        self.grid = GridLayout(spacing=dp(20), size_hint=(1, 1), padding=(dp(10), 0))
        
        nav_options = [
            {'title': 'Dashboard', 'screen_name': 'dashboard'},
            {'title': 'Inventory', 'screen_name': 'inventory'},
            {'title': 'Sales', 'screen_name': 'sales'},
            {'title': 'Customers', 'screen_name': 'customers'}
        ]
        for option in nav_options:
            card = NavigationCard(title=option['title'], screen_name=option['screen_name'])
            self.grid.add_widget(card)
        
        main_layout.add_widget(self.grid)
        self.add_widget(main_layout)

    def update_layout(self):
        # Switch between 1 and 2 columns based on window width
        if Window.width < self.breakpoint:
            self.grid.cols = 1
        else:
            self.grid.cols = 2
    
    def refresh_data(self):
        # No data to refresh here
        pass


# --- App Screens ---

class DashboardScreen(ResponsiveScreen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
        self.low_stock_threshold = 5

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        header_layout = BoxLayout(size_hint_y=None, height=dp(60))
        back_btn = ModernButton(text='Back', size_hint_x=None, width=dp(120))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'navigation'))
        header = Label(text='Dashboard', font_size=dp(24), bold=True, color=(0.1, 0.3, 0.5, 1))
        header_layout.add_widget(back_btn)
        header_layout.add_widget(header)
        main_layout.add_widget(header_layout)
        
        # FLEXIBLE: Grid will change columns
        self.stats_layout = GridLayout(cols=2, spacing=dp(15), size_hint_y=None)
        self.stats_layout.bind(minimum_height=self.stats_layout.setter('height'))
        main_layout.add_widget(self.stats_layout)
        
        activity_label = Label(text='Recent Sales', font_size=dp(18), bold=True, color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=dp(40))
        main_layout.add_widget(activity_label)
        
        scroll = ScrollView()
        self.activity_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.activity_layout.bind(minimum_height=self.activity_layout.setter('height'))
        scroll.add_widget(self.activity_layout)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def refresh_data(self):
        self.stats_layout.clear_widgets()
        self.activity_layout.clear_widgets()

        products = self.db_manager.get_all_products()
        customers = self.db_manager.get_all_customers()
        sales = self.db_manager.get_all_sales()

        total_products = len(products)
        total_customers = len(customers)
        total_sales = sum(sale['total'] for sale in sales)
        low_stock_items = len([p for p in products if p['stock'] <= self.low_stock_threshold])
        
        self.stats_layout.add_widget(ModernCard("Total Items", str(total_products)))
        self.stats_layout.add_widget(ModernCard("Total Customers", str(total_customers)))
        self.stats_layout.add_widget(ModernCard("Total Revenue", f"${total_sales:.2f}"))
        self.stats_layout.add_widget(ModernCard("Low Stock Alerts", str(low_stock_items)))
        
        for sale in sales[:5]:
            card = ModernCard(f"Sale #{sale['id']} - {sale['date']}", f"{sale['customer_name']} bought {sale['product_name']} - ${sale['total']:.2f}")
            self.activity_layout.add_widget(card)
    
    def update_layout(self):
        if hasattr(self, 'stats_layout'):
            if Window.width < self.breakpoint:
                self.stats_layout.cols = 1
            else:
                self.stats_layout.cols = 2

# (### NEW / REFACTORED ###) --- INVENTORY WIDGETS ---
class InventoryEntry(BoxLayout):
    """A responsive widget for a single inventory item."""
    def __init__(self, product, **kwargs):
        super().__init__(**kwargs)
        self.product = product
        self.low_stock_threshold = 2
        self.size_hint_y = None
        # Default to horizontal for desktop
        self.orientation = 'horizontal'
        self.spacing = dp(10)
        self.height = dp(140)

        details_text = f"Category: {product['category']}\n" \
                       f"Age: {product.get('age_range', 'N/A')} | Size: {product['size']}\n" \
                       f"Condition: {product.get('condition', 'N/A')}"
        
        self.card = ModernCard(title=f"{product['name']} - ${product['price']:.2f}", content=details_text)
        self.card.height = dp(140)

        stock_color = (0.9, 0.3, 0.3, 1) if product['stock'] <= self.low_stock_threshold else (0.2, 0.7, 0.2, 1)
        stock_status_text = f"Stock: {product['stock']}\n"
        stock_status_text += "LOW!" if product['stock'] <= self.low_stock_threshold else ""
        self.status_label = Label(text=stock_status_text, font_size=dp(12), color=stock_color, bold=True, size_hint_x=None, width=dp(80))
        
        self.buttons_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_x=None, width=dp(90))
        self.edit_btn = ModernButton(text='Edit', height=dp(40))
        self.delete_btn = Button(text='Delete', height=dp(40), background_normal='', background_color=(0.9, 0.3, 0.3, 1))
        self.buttons_layout.add_widget(self.edit_btn)
        self.buttons_layout.add_widget(self.delete_btn)
        
        self.add_widget(self.card)
        self.add_widget(self.status_label)
        self.add_widget(self.buttons_layout)

    def update_orientation(self, is_mobile):
        if is_mobile:
            # Switch to vertical for mobile
            self.orientation = 'vertical'
            self.height = dp(240)  # Taller to accommodate stacked widgets
            self.status_label.size_hint = (1, None) # Full width
            self.status_label.height = dp(40)
            self.buttons_layout.size_hint = (1, None) # Full width
            self.buttons_layout.height = dp(50)
            self.buttons_layout.orientation = 'horizontal' # Buttons side-by-side
        else:
            # Switch back to horizontal for desktop
            self.orientation = 'horizontal'
            self.height = dp(140)
            self.status_label.size_hint = (None, 1) # Fixed width
            self.status_label.width = dp(80)
            self.buttons_layout.size_hint = (None, 1) # Fixed width
            self.buttons_layout.width = dp(90)
            self.buttons_layout.orientation = 'vertical'


class InventoryScreen(ResponsiveScreen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        back_btn = ModernButton(text='Back', size_hint_x=None, width=dp(120))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'navigation'))
        header_label = Label(text='Inventory', font_size=dp(20), bold=True, color=(0.1, 0.3, 0.5, 1))
        add_btn = ModernButton(text='Add New', size_hint_x=None, width=dp(120))
        add_btn.bind(on_press=self.show_add_product_popup)
        header_layout.add_widget(back_btn)
        header_layout.add_widget(header_label)
        header_layout.add_widget(Widget())
        header_layout.add_widget(add_btn)
        main_layout.add_widget(header_layout)

        scroll = ScrollView()
        self.products_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.products_layout.bind(minimum_height=self.products_layout.setter('height'))
        scroll.add_widget(self.products_layout)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def refresh_data(self):
        self.products_layout.clear_widgets()
        products = self.db_manager.get_all_products()
        for product in products:
            entry = InventoryEntry(product)
            entry.edit_btn.bind(on_press=lambda x, p=product: self.show_edit_product_popup(p))
            entry.delete_btn.bind(on_press=lambda x, p=product: self.delete_product(p))
            self.products_layout.add_widget(entry)
        self.update_layout() # Ensure new items have correct layout

    def update_layout(self):
        is_mobile = Window.width < self.breakpoint
        for child in self.products_layout.children:
            if isinstance(child, InventoryEntry):
                child.update_orientation(is_mobile)
    
    # --- Popups and Data Logic (largely unchanged) ---
    def show_add_product_popup(self, instance):
        self.show_product_form_popup()
    
    def show_edit_product_popup(self, product):
        self.show_product_form_popup(product)
    
    def show_product_form_popup(self, product=None):
        popup_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        title = 'Edit Item' if product else 'Add New Item'
        
        name_input = ModernTextInput(hint_text='Product Name')
        category_spinner = Spinner(text='Select Category', values=['Bodysuits', 'Sleepwear', 'Outerwear', 'Dresses', 'Accessories'], size_hint_y=None, height=dp(40))
        age_ranges = ['Newborn', '0-3M', '3-6M', '6-9M', '9-12M', '12-18M', '18-24M','3A','Toddler']
        age_range_spinner = Spinner(text='Select Age Range', values=age_ranges, size_hint_y=None, height=dp(40))
        price_input = ModernTextInput(hint_text='Price (e.g., 24.99)')
        stock_input = ModernTextInput(hint_text='Stock Quantity')
        
        condition_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(5))
        condition_label = Label(text='Condition:', color=(0.2,0.2,0.2,1), size_hint_x=0.4)
        cb_new = CheckBox(group='condition', allow_no_selection=False, active=True, size_hint_x=0.1)
        cb_used = CheckBox(group='condition', allow_no_selection=False, size_hint_x=0.1)
        condition_layout.add_widget(condition_label)
        condition_layout.add_widget(cb_new)
        condition_layout.add_widget(Label(text='New', color=(0.2,0.2,0.2,1), size_hint_x=0.2))
        condition_layout.add_widget(cb_used)
        condition_layout.add_widget(Label(text='Used', color=(0.2,0.2,0.2,1), size_hint_x=0.2))

        if product:
            name_input.text = product['name']
            category_spinner.text = product['category']
            age_range_spinner.text = product.get('age_range', 'Select Age Range')
            price_input.text = str(product['price'])
            stock_input.text = str(product['stock'])
            cb_used.active = product.get('condition') == 'Gently Used'

        popup_layout.add_widget(Label(text=title, font_size=dp(18), bold=True, size_hint_y=None, height=dp(40), color=(0.2,0.2,0.2,1)))
        popup_layout.add_widget(name_input)
        popup_layout.add_widget(category_spinner)
        popup_layout.add_widget(age_range_spinner)
        popup_layout.add_widget(price_input)
        popup_layout.add_widget(stock_input)
        popup_layout.add_widget(condition_layout)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        save_btn = ModernButton(text='Save Item')
        cancel_btn = Button(text='Cancel', background_normal='', background_color=(0.7, 0.7, 0.7, 1))
        buttons_layout.add_widget(save_btn)
        buttons_layout.add_widget(cancel_btn)
        popup_layout.add_widget(buttons_layout)
        
        popup = Popup(title='', content=popup_layout, size_hint=(0.9, 0.9), separator_height=0)
        
        def save_product(instance):
            try:
                product_data = {
                    'name': name_input.text, 'category': category_spinner.text, 'price': float(price_input.text),
                    'stock': int(stock_input.text), 'condition': 'Gently Used' if cb_used.active else 'New',
                    'age_range': age_range_spinner.text, 'size': age_range_spinner.text,
                    'color': product.get('color', 'N/A') if product else 'N/A', 
                    'material': product.get('material', 'N/A') if product else 'N/A',
                    'supplier': product.get('supplier', 'N/A') if product else 'N/A',
                }
                if product:
                    product_data['id'] = product['id']
                    self.db_manager.update_product(product_data)
                else:
                    self.db_manager.add_product(product_data)
                
                self.refresh_data()
                popup.dismiss()
            except ValueError:
                # Add error feedback here if desired
                pass
        
        save_btn.bind(on_press=save_product)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def delete_product(self, product):
        self.db_manager.delete_product(product['id'])
        self.refresh_data()


# SalesScreen and CustomersScreen remain simple and are now responsive via the base class
class SalesScreen(ResponsiveScreen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        back_btn = ModernButton(text='Back', size_hint_x=None, width=dp(120))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'navigation'))
        header_label = Label(text='Sales Records', font_size=dp(20), bold=True, color=(0.1, 0.3, 0.5, 1))
        add_sale_btn = ModernButton(text='Add Sale', size_hint_x=None, width=dp(120))
        add_sale_btn.bind(on_press=self.show_add_sale_popup)
        header_layout.add_widget(back_btn)
        header_layout.add_widget(header_label)
        header_layout.add_widget(Widget())
        header_layout.add_widget(add_sale_btn)
        main_layout.add_widget(header_layout)

        scroll = ScrollView()
        self.sales_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.sales_layout.bind(minimum_height=self.sales_layout.setter('height'))
        scroll.add_widget(self.sales_layout)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def refresh_data(self):
        self.sales_layout.clear_widgets()
        sales = self.db_manager.get_all_sales()
        if not sales:
            self.sales_layout.add_widget(Label(text="No sales records found.", color=(0.5,0.5,0.5,1)))
        for sale in sales:
            sale_content = f"Customer: {sale['customer_name']}\nProduct: {sale['product_name']} (x{sale['quantity']})\nTotal: ${sale['total']:.2f}"
            card = ModernCard(title=f"Sale #{sale['id']} - {sale['date']}", content=sale_content)
            card.height = dp(140)
            self.sales_layout.add_widget(card)
    
    def update_layout(self):
        pass # No specific layout changes needed for this screen

    def show_add_sale_popup(self, instance):
        # This popup logic remains the same
        popup_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        customers = self.db_manager.get_all_customers()
        products = self.db_manager.get_all_products()
        customer_names = [c['name'] for c in customers]
        product_names = [p['name'] for p in products if p['stock'] > 0]

        customer_spinner = Spinner(text='Select Customer', values=customer_names, size_hint_y=None, height=dp(40))
        product_spinner = Spinner(text='Select Product', values=product_names, size_hint_y=None, height=dp(40))
        quantity_input = ModernTextInput(hint_text='Quantity', input_filter='int')
        date_input = ModernTextInput(hint_text='Date (YYYY-MM-DD)', text=datetime.date.today().isoformat())
        
        popup_layout.add_widget(Label(text='Record New Sale', font_size=dp(18), bold=True, size_hint_y=None, height=dp(40), color=(0.2,0.2,0.2,1)))
        popup_layout.add_widget(date_input)
        popup_layout.add_widget(customer_spinner)
        popup_layout.add_widget(product_spinner)
        popup_layout.add_widget(quantity_input)

        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        save_btn = ModernButton(text='Save Sale')
        cancel_btn = Button(text='Cancel', background_normal='', background_color=(0.7, 0.7, 0.7, 1))
        buttons_layout.add_widget(save_btn)
        buttons_layout.add_widget(cancel_btn)
        popup_layout.add_widget(buttons_layout)

        popup = Popup(title='', content=popup_layout, size_hint=(0.9, 0.8), separator_height=0)

        def save_sale(instance):
            try:
                customer_name = customer_spinner.text
                product_name = product_spinner.text
                quantity = int(quantity_input.text)
                
                product = next(p for p in products if p['name'] == product_name)
                customer = next(c for c in customers if c['name'] == customer_name)

                if quantity > product['stock']: return

                new_sale = {
                    'date': date_input.text, 'customer': customer_name, 'product': product_name, 'quantity': quantity,
                    'total': quantity * product['price'], 'size': product.get('size', 'N/A')
                }
                self.db_manager.add_sale(new_sale, product['id'], customer['id'])
                self.refresh_data()
                popup.dismiss()
            except (ValueError, StopIteration):
                pass
        
        save_btn.bind(on_press=save_sale)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()


class CustomersScreen(ResponsiveScreen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        back_btn = ModernButton(text='Back', size_hint_x=None, width=dp(120))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'navigation'))
        header_label = Label(text='Customers', font_size=dp(20), bold=True, color=(0.1, 0.3, 0.5, 1))
        add_btn = ModernButton(text='Add Customer', size_hint_x=None, width=dp(140))
        add_btn.bind(on_press=self.show_add_customer_popup)
        header_layout.add_widget(back_btn)
        header_layout.add_widget(header_label)
        header_layout.add_widget(Widget())
        header_layout.add_widget(add_btn)
        main_layout.add_widget(header_layout)
        scroll = ScrollView()
        self.customers_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.customers_layout.bind(minimum_height=self.customers_layout.setter('height'))
        scroll.add_widget(self.customers_layout)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def refresh_data(self):
        self.customers_layout.clear_widgets()
        customers = self.db_manager.get_all_customers()
        for customer in customers:
            customer_content = f"Email: {customer['email']}\nPhone: {customer['phone']}\nBaby: {customer['baby_name']} ({customer['baby_age']})"
            card = ModernCard(title=f"{customer['name']} - Total Spent: ${customer['total_purchases']:.2f}", content=customer_content)
            card.height = dp(140)
            self.customers_layout.add_widget(card)

    def update_layout(self):
        pass # No layout changes needed
    
    def show_add_customer_popup(self, instance):
        # This popup logic remains the same
        popup_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        name_input = ModernTextInput(hint_text='Customer Name')
        email_input = ModernTextInput(hint_text='Email')
        phone_input = ModernTextInput(hint_text='Phone')
        baby_name_input = ModernTextInput(hint_text='Baby Name')
        baby_age_input = ModernTextInput(hint_text='Baby Age')
        popup_layout.add_widget(Label(text='Add New Customer', font_size=dp(18), bold=True, size_hint_y=None, height=dp(40), color=(0.2,0.2,0.2,1)))
        popup_layout.add_widget(name_input)
        popup_layout.add_widget(email_input)
        popup_layout.add_widget(phone_input)
        popup_layout.add_widget(baby_name_input)
        popup_layout.add_widget(baby_age_input)
        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        save_btn = ModernButton(text='Save Customer')
        cancel_btn = Button(text='Cancel', background_normal='', background_color=(0.7, 0.7, 0.7, 1))
        buttons_layout.add_widget(save_btn)
        buttons_layout.add_widget(cancel_btn)
        popup_layout.add_widget(buttons_layout)
        popup = Popup(title='', content=popup_layout, size_hint=(0.9, 0.9), separator_height=0)

        def save_customer(instance):
            new_customer = {
                'name': name_input.text, 'email': email_input.text, 'phone': phone_input.text,
                'baby_name': baby_name_input.text, 'baby_age': baby_age_input.text
            }
            if new_customer['name']:
                self.db_manager.add_customer(new_customer)
                self.refresh_data()
                popup.dismiss()
        
        save_btn.bind(on_press=save_customer)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

class BabyClothesStoreApp(App):
    def build(self):
        self.title = 'Store Management System'
        Window.clearcolor = (1, 1, 1, 1)
        self.db_manager = DatabaseManager()

        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(NavigationScreen(name='navigation'))
        sm.add_widget(DashboardScreen(self.db_manager, name='dashboard'))
        sm.add_widget(InventoryScreen(self.db_manager, name='inventory'))
        sm.add_widget(SalesScreen(self.db_manager, name='sales'))
        sm.add_widget(CustomersScreen(self.db_manager, name='customers'))
        sm.current = 'navigation'
        return sm

if __name__ == '__main__':
    BabyClothesStoreApp().run()