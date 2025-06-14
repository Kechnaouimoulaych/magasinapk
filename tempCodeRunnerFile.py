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
import json
import datetime

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
        
        title_label = Label(
            text=title,
            font_size=dp(16),
            bold=True,
            color=(0.2, 0.2, 0.2, 1), 
            size_hint_y=0.4,
            text_size=(self.width - dp(30), None),
            halign='left',
            valign='top'
        )
        self.add_widget(title_label)
        
        content_label = Label(
            text=content,
            font_size=dp(14),
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=0.6,
            text_size=(self.width - dp(30), None),
            halign='left',
            valign='top'
        )
        self.add_widget(content_label)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        for child in self.children:
            if isinstance(child, Label):
                child.text_size = (self.width - dp(30), None)

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

# --- Data Store (Added 'age_range') ---
class DataStore:
    def __init__(self):
        self.products = []
        self.customers = []
        self.sales = []
        self.low_stock_threshold = 5
        self.init_sample_data()
    
    def init_sample_data(self):
        self.products = [
            # (### NEW ###) Added 'age_range' field
            {"id": 1, "name": "Baby Onesie Set", "category": "Bodysuits", "price": 24.99, "stock": 15, "supplier": "Baby Comfort Co", "size": "0-3M", "age_range": "0-3M", "color": "Pink", "material": "Cotton", "condition": "New"},
            {"id": 2, "name": "Infant Sleep Gown", "category": "Sleepwear", "price": 18.99, "stock": 8, "supplier": "Sleepy Baby", "size": "3-6M", "age_range": "3-6M", "color": "Blue", "material": "Organic Cotton", "condition": "New"},
            {"id": 3, "name": "Newborn Romper", "category": "Outerwear", "price": 32.99, "stock": 12, "supplier": "Little Angels", "size": "Newborn", "age_range": "Newborn", "color": "Yellow", "material": "Bamboo", "condition": "Gently Used"},
            {"id": 4, "name": "Baby Footie Pajamas", "category": "Sleepwear", "price": 22.99, "stock": 4, "supplier": "Cozy Dreams", "size": "6-9M", "age_range": "6-9M", "color": "White", "material": "Cotton Blend", "condition": "New"},
        ]
        self.customers = [
            {"id": 1, "name": "Emma Johnson", "email": "emma.j@email.com", "phone": "123-456-7890", "total_purchases": 89.97, "baby_name": "Lily", "baby_age": "3 months"},
            {"id": 2, "name": "Sarah Williams", "email": "sarah.w@email.com", "phone": "098-765-4321", "total_purchases": 156.94, "baby_name": "Max", "baby_age": "8 months"},
        ]
        self.sales = [
            {"id": 1, "date": "2024-06-10", "customer": "Emma Johnson", "product": "Baby Onesie Set", "quantity": 2, "total": 49.98, "size": "0-3M"},
            {"id": 2, "date": "2024-06-12", "customer": "Sarah Williams", "product": "Infant Sleep Gown", "quantity": 3, "total": 56.97, "size": "3-6M"},
        ]

# --- Navigation Widgets (No changes here) ---

class NavigationCard(ButtonBehavior, BoxLayout):
    def __init__(self, title, screen_name, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(15)
        self.size_hint = (None, None)
        self.size = (dp(250), dp(150))
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

class NavigationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(20))
        header = Label(text='Store Management System', font_size=dp(32), bold=True, color=(0.1, 0.3, 0.5, 1), size_hint_y=None, height=dp(80))
        main_layout.add_widget(header)
        grid = GridLayout(cols=2, spacing=dp(30), size_hint=(None, None), size=(dp(530), dp(330)))
        grid.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        nav_options = [
            {'title': 'Dashboard', 'screen_name': 'dashboard'},
            {'title': 'Inventory', 'screen_name': 'inventory'},
            {'title': 'Sales', 'screen_name': 'sales'},
            {'title': 'Customers', 'screen_name': 'customers'}
        ]
        for option in nav_options:
            card = NavigationCard(title=option['title'], screen_name=option['screen_name'])
            grid.add_widget(card)
        main_layout.add_widget(grid)
        self.add_widget(main_layout)

# --- App Screens ---

class DashboardScreen(Screen):
    # This screen will now refresh on_enter to reflect new sales data
    def __init__(self, data_store, **kwargs):
        super().__init__(**kwargs)
        self.data_store = data_store
    def on_enter(self, *args):
        self.clear_widgets() 
        self.build_dashboard()
    def build_dashboard(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        header_layout = BoxLayout(size_hint_y=None, height=dp(60))
        back_btn = ModernButton(text='Back to Menu', size_hint_x=None, width=dp(180))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'navigation'))
        header = Label(text='Dashboard', font_size=dp(24), bold=True, color=(0.1, 0.3, 0.5, 1))
        header_layout.add_widget(back_btn)
        header_layout.add_widget(header)
        main_layout.add_widget(header_layout)
        
        stats_layout = GridLayout(cols=2, spacing=dp(15), size_hint_y=None, height=dp(270))
        total_products = len(self.data_store.products)
        total_customers = len(self.data_store.customers)
        total_sales = sum(sale['total'] for sale in self.data_store.sales)
        low_stock_items = len([p for p in self.data_store.products if p['stock'] <= self.data_store.low_stock_threshold])
        stats_layout.add_widget(ModernCard("Total Items", str(total_products)))
        stats_layout.add_widget(ModernCard("Total Customers", str(total_customers)))
        stats_layout.add_widget(ModernCard("Total Revenue", f"${total_sales:.2f}"))
        stats_layout.add_widget(ModernCard("Low Stock Alerts", str(low_stock_items)))
        main_layout.add_widget(stats_layout)
        
        activity_label = Label(text='Recent Sales', font_size=dp(18), bold=True, color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=dp(40))
        main_layout.add_widget(activity_label)
        scroll = ScrollView()
        activity_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        activity_layout.bind(minimum_height=activity_layout.setter('height'))
        for sale in reversed(self.data_store.sales[-5:]): # Show newest first
            activity_card = ModernCard(f"Sale #{sale['id']} - {sale['date']}", f"{sale['customer']} bought {sale['product']} - ${sale['total']:.2f}")
            activity_layout.add_widget(activity_card)
        scroll.add_widget(activity_layout)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

class InventoryScreen(Screen):
    def __init__(self, data_store, **kwargs):
        super().__init__(**kwargs)
        self.data_store = data_store
    def on_enter(self, *args):
        self.clear_widgets()
        self.build_inventory()
    def build_inventory(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        back_btn = ModernButton(text='Back', size_hint_x=None, width=dp(120))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'navigation'))
        header_label = Label(text='Inventory', font_size=dp(20), bold=True, color=(0.1, 0.3, 0.5, 1))
        add_btn = ModernButton(text='Add New Item', size_hint_x=None, width=dp(140))
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
        self.refresh_products_list()

    def refresh_products_list(self):
        self.products_layout.clear_widgets()
        for product in self.data_store.products:
            # Using ModernCard for a more consistent look
            # (### CHANGED ###) Added 'Age' to the details display
            details_text = f"Category: {product['category']}\n" \
                           f"Age: {product.get('age_range', 'N/A')} | Size: {product['size']}\n" \
                           f"Condition: {product.get('condition', 'N/A')}"
            
            # Using ModernCard makes the layout cleaner
            card = ModernCard(title=f"{product['name']} - ${product['price']:.2f}", content=details_text)
            card.height = dp(140)

            # Layout to hold the card and buttons
            product_entry_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(140), spacing=dp(10))
            
            stock_color = (0.9, 0.3, 0.3, 1) if product['stock'] <= self.data_store.low_stock_threshold else (0.2, 0.7, 0.2, 1)
            stock_status_text = f"Stock: {product['stock']}\n"
            stock_status_text += "LOW!" if product['stock'] <= self.data_store.low_stock_threshold else ""
            status_label = Label(text=stock_status_text, font_size=dp(12), color=stock_color, bold=True, size_hint_x=None, width=dp(80))
            
            buttons_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_x=None, width=dp(90))
            edit_btn = ModernButton(text='Edit', height=dp(40))
            edit_btn.bind(on_press=lambda x, p=product: self.show_edit_product_popup(p))
            delete_btn = Button(text='Delete', height=dp(40), background_normal='', background_color=(0.9, 0.3, 0.3, 1))
            delete_btn.bind(on_press=lambda x, p=product: self.delete_product(p))
            buttons_layout.add_widget(edit_btn)
            buttons_layout.add_widget(delete_btn)
            
            product_entry_layout.add_widget(card)
            product_entry_layout.add_widget(status_label)
            product_entry_layout.add_widget(buttons_layout)
            
            self.products_layout.add_widget(product_entry_layout)

    def show_add_product_popup(self, instance):
        self.show_product_form_popup()
    
    def show_edit_product_popup(self, product):
        self.show_product_form_popup(product)
    
    def show_product_form_popup(self, product=None):
        popup_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        title = 'Edit Item' if product else 'Add New Item'
        
        name_input = ModernTextInput(hint_text='Product Name')
        category_spinner = Spinner(text='Select Category', values=['Bodysuits', 'Sleepwear', 'Outerwear', 'Dresses', 'Accessories'], size_hint_y=None, height=dp(40))
        
        # (### NEW ###) Age Range Spinner
        age_ranges = ['Newborn', '0-3M', '3-6M', '6-9M', '9-12M', '12-18M', '18-24M', 'Toddler']
        age_range_spinner = Spinner(text='Select Age Range', values=age_ranges, size_hint_y=None, height=dp(40))

        price_input = ModernTextInput(hint_text='Price (e.g., 24.99)')
        stock_input = ModernTextInput(hint_text='Stock Quantity')
        
        condition_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        condition_label = Label(text='Condition:', color=(0.2,0.2,0.2,1))
        new_check_layout = BoxLayout(spacing=dp(5))
        cb_new = CheckBox(group='condition', allow_no_selection=False, active=True)
        new_check_layout.add_widget(cb_new)
        new_check_layout.add_widget(Label(text='New', color=(0.2,0.2,0.2,1)))
        used_check_layout = BoxLayout(spacing=dp(5))
        cb_used = CheckBox(group='condition', allow_no_selection=False)
        used_check_layout.add_widget(cb_used)
        used_check_layout.add_widget(Label(text='Gently Used', color=(0.2,0.2,0.2,1)))
        condition_layout.add_widget(condition_label)
        condition_layout.add_widget(new_check_layout)
        condition_layout.add_widget(used_check_layout)
        
        if product:
            name_input.text = product['name']
            category_spinner.text = product['category']
            age_range_spinner.text = product.get('age_range', 'Select Age Range') # (### NEW ###)
            price_input.text = str(product['price'])
            stock_input.text = str(product['stock'])
            if product.get('condition') == 'Gently Used':
                cb_used.active = True
            else:
                cb_new.active = True

        popup_layout.add_widget(Label(text=title, font_size=dp(18), bold=True, size_hint_y=None, height=dp(40), color=(0.2,0.2,0.2,1)))
        popup_layout.add_widget(name_input)
        popup_layout.add_widget(category_spinner)
        popup_layout.add_widget(age_range_spinner) # (### NEW ###) Add spinner to layout
        popup_layout.add_widget(price_input)
        popup_layout.add_widget(stock_input)
        popup_layout.add_widget(condition_layout)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        save_btn = ModernButton(text='Save Item')
        cancel_btn = Button(text='Cancel', background_normal='', background_color=(0.7, 0.7, 0.7, 1))
        buttons_layout.add_widget(save_btn)
        buttons_layout.add_widget(cancel_btn)
        popup_layout.add_widget(buttons_layout)
        
        popup = Popup(title='', content=popup_layout, size_hint=(0.8, 0.9), separator_height=0)
        
        def save_product(instance):
            try:
                selected_condition = 'New' if cb_new.active else 'Gently Used'
                new_product_data = {
                    'name': name_input.text,
                    'category': category_spinner.text,
                    'age_range': age_range_spinner.text, # (### NEW ###) Save age range
                    'price': float(price_input.text),
                    'stock': int(stock_input.text),
                    'condition': selected_condition,
                    'size': product.get('size', age_range_spinner.text) if product else age_range_spinner.text, # Use age range for size if not specified
                    'color': product.get('color', 'N/A') if product else 'N/A',
                    'material': product.get('material', 'N/A') if product else 'N/A',
                    'supplier': product.get('supplier', 'N/A') if product else 'N/A',
                }
                if product:
                    new_product_data['id'] = product['id']
                    idx = next(i for i, p in enumerate(self.data_store.products) if p['id'] == product['id'])
                    self.data_store.products[idx] = new_product_data
                else:
                    new_product_data['id'] = max([p['id'] for p in self.data_store.products], default=0) + 1
                    self.data_store.products.append(new_product_data)
                
                self.refresh_products_list()
                popup.dismiss()
            except (ValueError, StopIteration):
                pass
        
        save_btn.bind(on_press=save_product)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def delete_product(self, product):
        self.data_store.products = [p for p in self.data_store.products if p['id'] != product['id']]
        self.refresh_products_list()

# (### MAJOR CHANGES ###) --- SALES SCREEN WITH "ADD SALE" FUNCTIONALITY ---

class SalesScreen(Screen):
    def __init__(self, data_store, **kwargs):
        super().__init__(**kwargs)
        self.data_store = data_store
    def on_enter(self, *args):
        self.clear_widgets()
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        back_btn = ModernButton(text='Back', size_hint_x=None, width=dp(120))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'navigation'))
        header_label = Label(text='Sales Records', font_size=dp(20), bold=True, color=(0.1, 0.3, 0.5, 1))
        
        # (### NEW ###) Add Sale Button
        add_sale_btn = ModernButton(text='Add Sale', size_hint_x=None, width=dp(120))
        add_sale_btn.bind(on_press=self.show_add_sale_popup)

        header_layout.add_widget(back_btn)
        header_layout.add_widget(header_label)
        header_layout.add_widget(Widget())
        header_layout.add_widget(add_sale_btn) # (### NEW ###)
        main_layout.add_widget(header_layout)

        scroll = ScrollView()
        self.sales_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.sales_layout.bind(minimum_height=self.sales_layout.setter('height'))
        scroll.add_widget(self.sales_layout)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)
        self.refresh_sales_list() # (### CHANGED ###) Use a refresh method

    def refresh_sales_list(self):
        self.sales_layout.clear_widgets()
        if not self.data_store.sales:
            self.sales_layout.add_widget(Label(text="No sales records found.", color=(0.5,0.5,0.5,1)))
        for sale in reversed(self.data_store.sales):
            sale_content = f"Customer: {sale['customer']}\n" \
                           f"Product: {sale['product']} (x{sale['quantity']})\n" \
                           f"Total: ${sale['total']:.2f}"
            card = ModernCard(title=f"Sale #{sale['id']} - {sale['date']}", content=sale_content)
            card.height = dp(140)
            self.sales_layout.add_widget(card)

    def show_add_sale_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        customer_names = [c['name'] for c in self.data_store.customers]
        product_names = [p['name'] for p in self.data_store.products if p['stock'] > 0] # Only show items in stock

        customer_spinner = Spinner(text='Select Customer', values=customer_names, size_hint_y=None, height=dp(40))
        product_spinner = Spinner(text='Select Product', values=product_names, size_hint_y=None, height=dp(40))
        quantity_input = ModernTextInput(hint_text='Quantity', input_filter='int')
        
        popup_layout.add_widget(Label(text='Record New Sale', font_size=dp(18), bold=True, size_hint_y=None, height=dp(40), color=(0.2,0.2,0.2,1)))
        popup_layout.add_widget(customer_spinner)
        popup_layout.add_widget(product_spinner)
        popup_layout.add_widget(quantity_input)

        buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        save_btn = ModernButton(text='Save Sale')
        cancel_btn = Button(text='Cancel', background_normal='', background_color=(0.7, 0.7, 0.7, 1))
        buttons_layout.add_widget(save_btn)
        buttons_layout.add_widget(cancel_btn)
        popup_layout.add_widget(buttons_layout)

        popup = Popup(title='', content=popup_layout, size_hint=(0.8, 0.7), separator_height=0)

        def save_sale(instance):
            try:
                customer_name = customer_spinner.text
                product_name = product_spinner.text
                quantity = int(quantity_input.text)

                # Validation
                if customer_name == 'Select Customer' or product_name == 'Select Product' or quantity <= 0:
                    self.show_error_popup("Please fill all fields with valid data.")
                    return
                
                product = next(p for p in self.data_store.products if p['name'] == product_name)
                customer = next(c for c in self.data_store.customers if c['name'] == customer_name)

                # Stock check
                if quantity > product['stock']:
                    self.show_error_popup(f"Not enough stock for {product_name}.\nAvailable: {product['stock']}")
                    return

                # Update data
                product['stock'] -= quantity
                total_price = quantity * product['price']
                customer['total_purchases'] += total_price

                new_sale = {
                    'id': max([s['id'] for s in self.data_store.sales], default=0) + 1,
                    'date': datetime.date.today().isoformat(),
                    'customer': customer_name,
                    'product': product_name,
                    'quantity': quantity,
                    'total': total_price,
                    'size': product.get('size', 'N/A')
                }
                self.data_store.sales.append(new_sale)

                self.refresh_sales_list() # Refresh this screen's list
                popup.dismiss()

            except (ValueError, StopIteration):
                self.show_error_popup("Invalid input. Please check all fields.")
        
        save_btn.bind(on_press=save_sale)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def show_error_popup(self, message):
        # Helper for showing error messages
        popup_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        popup_layout.add_widget(Label(text=message, color=(0.8,0,0,1)))
        ok_button = ModernButton(text='OK', height=dp(40))
        popup_layout.add_widget(ok_button)
        error_popup = Popup(title='Error', content=popup_layout, size_hint=(0.6, 0.4))
        ok_button.bind(on_press=error_popup.dismiss)
        error_popup.open()


class CustomersScreen(Screen):
    # This screen now uses the refresh pattern for consistency
    def __init__(self, data_store, **kwargs):
        super().__init__(**kwargs)
        self.data_store = data_store
    def on_enter(self, *args):
        self.clear_widgets()
        self.build_ui()
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
        self.refresh_customers_list()
    def refresh_customers_list(self):
        self.customers_layout.clear_widgets()
        for customer in self.data_store.customers:
            customer_content = f"Email: {customer['email']}\n" \
                               f"Phone: {customer['phone']}\n" \
                               f"Baby: {customer['baby_name']} ({customer['baby_age']})"
            card = ModernCard(title=f"{customer['name']} - Total Spent: ${customer['total_purchases']:.2f}", content=customer_content)
            card.height = dp(140)
            self.customers_layout.add_widget(card)
    def show_add_customer_popup(self, instance):
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
        popup = Popup(title='', content=popup_layout, size_hint=(0.8, 0.9), separator_height=0)
        def save_customer(instance):
            new_customer = {'id': max([c['id'] for c in self.data_store.customers], default=0) + 1, 'name': name_input.text, 'email': email_input.text, 'phone': phone_input.text, 'total_purchases': 0, 'baby_name': baby_name_input.text, 'baby_age': baby_age_input.text}
            if new_customer['name']:
                self.data_store.customers.append(new_customer)
                self.refresh_customers_list()
                popup.dismiss()
        save_btn.bind(on_press=save_customer)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

class BabyClothesStoreApp(App):
    def build(self):
        self.title = 'Store Management System'
        Window.clearcolor = (1, 1, 1, 1)
        self.data_store = DataStore()
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(NavigationScreen(name='navigation'))
        sm.add_widget(DashboardScreen(self.data_store, name='dashboard'))
        sm.add_widget(InventoryScreen(self.data_store, name='inventory'))
        sm.add_widget(SalesScreen(self.data_store, name='sales'))
        sm.add_widget(CustomersScreen(self.data_store, name='customers'))
        sm.current = 'navigation'
        return sm

if __name__ == '__main__':
    BabyClothesStoreApp().run()