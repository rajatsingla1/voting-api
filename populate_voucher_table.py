import datetime
from getpass import getpass
from mysql.connector import connect, Error


def populate_voucher_codes_table(cursor, conn):
    f = open("brasenose_voucher_codes.txt")
    lines = f.readlines()

    for line in lines:
        voucher_code = line
        expiry_date = datetime.datetime(2023, 3, 10)

        insert_new_voucher_query = f"""
                INSERT INTO voucher_codes (Voucher, ExpiryDate, Used) VALUES ({voucher_code}, '{expiry_date}', false)
                """

        print("Executing query: " + insert_new_voucher_query)
        cursor.execute(insert_new_voucher_query)

    conn.commit()


try:
    with connect(
        host="localhost",
        user="root",
        password=getpass("Please enter MySQL password: ")
    ) as connection:
        with connection.cursor() as cursor:
            populate_voucher_codes_table(cursor, connection)
except Error as e:
    print(e)