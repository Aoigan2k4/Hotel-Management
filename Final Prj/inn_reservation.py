import mysql.connector
import sys
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='tomtin1212',
    database='inn_reservation'
)

cursor = conn.cursor()
# cursor.execute("DROP DATABASE inn_reservation")
# cursor.execute("CREATE DATABASE inn_reservation")

# inn_customer table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS inn_customer (
        c_id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        email VARCHAR(30),
        phone_number BIGINT
    )
''')

# inn_rooms table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS inn_rooms (
        r_id INT AUTO_INCREMENT PRIMARY KEY,
        room_type VARCHAR(1),
        room_price DECIMAL(8,2),
        availability SMALLINT
    )
''')

# inn_reservation table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Inn_reservation (
        cr_id INT AUTO_INCREMENT PRIMARY KEY,
        r_id INT,
        c_id INT,
        accommodation_days SMALLINT,
        cost DECIMAL(8,2),
        checkout TINYINT(1),
        FOREIGN KEY (c_id) REFERENCES inn_customer(c_id),
        FOREIGN KEY (r_id) REFERENCES inn_rooms(r_id)
    )
''')
cursor.execute("DELETE FROM Inn_reservation")
cursor.execute("ALTER TABLE Inn_reservation AUTO_INCREMENT = 1")

cursor.execute("DELETE FROM inn_rooms")
cursor.execute("ALTER TABLE inn_rooms AUTO_INCREMENT = 1")
               
cursor.execute("DELETE FROM inn_customer")
cursor.execute("ALTER TABLE inn_customer AUTO_INCREMENT = 1")


# Populate inn_rooms
insert_room = "INSERT INTO inn_rooms (room_type, room_price, availability) VALUES (%s, %s, %s)" 
room_data = [
    ('S', 70.00, 10),
    ('P', 120.00, 8),
    ('O', 200.00, 9),
    ('E', 250.00, 5)
]  
cursor.executemany(insert_room, room_data) 
    

with open('reservation_file.txt', 'r') as file:
    for line in file:
        data = line.strip().split(',')
        first_name, last_name, email, phone_number, room_type, accommodation_days = data
        
        # Populate inn_customer
        insert_customer = "INSERT INTO inn_customer (first_name, last_name, email, phone_number) VALUES(%s, %s, %s, %s)"
        customer_data = (first_name, last_name, email, phone_number)
        cursor.execute(insert_customer, customer_data)
        
        # c_id from inn_customer
        cursor.execute("SELECT c_id FROM inn_customer WHERE first_name = %s AND last_name = %s AND email = %s AND phone_number = %s", (first_name, last_name, email, phone_number))
        customer_id = cursor.fetchone()[0]
        
        # Room_price and r_id from inn_room
        cursor.execute("SELECT r_id, room_price FROM inn_rooms WHERE room_type = %s", (room_type,))
        room_data = cursor.fetchone()
        room_id = room_data[0]
        price = room_data[1]
        
        # Cost calculation
        cost = int(accommodation_days) * price
        
        # Populate Inn_reservation
        insert_reservation = "INSERT INTO Inn_reservation (r_id, c_id, accommodation_days, cost, checkout) VALUES(%s, %s, %s, %s, %s)"
        reservation_data = [room_id, customer_id, int(accommodation_days), cost, 0]
        cursor.execute(insert_reservation, reservation_data)

# Interfaces
print("\t**************Welcome to the LIRS system !**************\t")
print("Please select the folowing options to continue" + 
      "\n1. Check-out"
      "\n2. Check-in"
      "\n3. Exit")
choice = input("Your choice:")

if choice == '1':
    print("************Check-out Process************")
    phone_number = input("Enter your phone number:")
    print("Cheking out....")
    query = "SELECT c_id, first_name, last_name FROM inn_customer where phone_number = %s"
    cursor.execute(query,(phone_number,))
    cust_data = cursor.fetchone()
    
    if cust_data:
        cust_id = cust_data[0]
        cust_first = cust_data[1]
        cust_last = cust_data[2]
        checkout_update = "UPDATE Inn_reservation SET checkout = %s WHERE c_id = %s"
        cursor.execute(checkout_update, (1, cust_id,))  
        
        cursor.execute("SELECT r_id, cost, accommodation_days FROM Inn_reservation WHERE c_id = %s", (cust_id,))
        r_data = cursor.fetchone()
        r_id = r_data[0]
        r_cost = r_data[1]
        r_stay = r_data[2]

        cursor.execute("SELECT room_type FROM inn_rooms WHERE r_id = %s", (r_id,))
        room_data = cursor.fetchone()
        r_type = room_data[0]
        
        # Update availability 
        cursor.execute("UPDATE inn_rooms SET availability = availability + 1 WHERE r_id = %s", (r_id,))
        
        conn.commit()
        print("-------------Pacific Inn-------------")
        print("Your invoice is:"
              f"\nName: {cust_first}{cust_last}"
              f"\nDuration: {r_stay} days"
              f"\nRoom type: {r_type}"
              f"\nTotal: ${r_cost}")
        print("\n------------- Thank You! See you next time -------------")
    else:
        print("Customer not found!")
elif choice == '2':
    print("************Check-in Process************")
    phone_number = input("Enter your phone number:")
    print("Cheking in....")
    query = "SELECT c_id, first_name, last_name FROM inn_customer where phone_number = %s"
    cursor.execute(query,(phone_number,))
    cust_data = cursor.fetchone()
    
    if cust_data:
        cust_id = cust_data[0]
        cust_first = cust_data[1]
        cust_last = cust_data[2]
        checkout_update = "UPDATE Inn_reservation SET checkout = %s WHERE c_id = %s"
        cursor.execute(checkout_update, (0, cust_id,))  
        
        cursor.execute("SELECT r_id, cost, accommodation_days FROM Inn_reservation WHERE c_id = %s", (cust_id,))
        r_data = cursor.fetchone()
        r_id = r_data[0]
        r_cost = r_data[1]
        r_stay = r_data[2]

        cursor.execute("SELECT room_type FROM inn_rooms WHERE r_id = %s", (r_id,))
        room_data = cursor.fetchone()
        r_type = room_data[0]
        
        # Update availability 
        cursor.execute("UPDATE inn_rooms SET availability = availability - 1 WHERE r_id = %s", (r_id,))
        
        conn.commit()
        print("Check-in successfully!")
        print("\n------------- Enjoy Your Stay! -------------")
    else:
        print("Customer not found!")
elif choice == '3':
    sys.exit()
    
def view_table(table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    result = cursor.fetchall()
    print(f"\nTable: {table_name}")
    for row in result:
        print(row)


# View inn_customer table
view_table('inn_customer')

# View inn_rooms table
view_table('inn_rooms')

# View Inn_reservation table
view_table('Inn_reservation')

conn.commit()
cursor.close()
conn.close()
