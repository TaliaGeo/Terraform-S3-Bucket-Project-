import os
import csv
from datetime import datetime
import sys
import mysql.connector

class DeploymentTracker:
    def get_records(self):
        return self.records

    def __init__(self):
        self.records = []
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="taliageo",
            password="Talia992004",
            database="mydatabase"
        )
        self.mycursor = self.mydb.cursor()
        self.create_table()

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS deployments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Application VARCHAR(255),
            Environment VARCHAR(255),
            Version VARCHAR(50),
            DeploymentDate DATE,
            DeployedBy VARCHAR(255)
        )
        """
        self.mycursor.execute(create_table_query)
        self.mydb.commit()
        print("Table 'deployments' is ready.")

    def read_records(self, file_path):
        try:
            if not file_path.endswith(".csv"):
                raise ValueError("Error: The file is not a CSV file.")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Error: File '{file_path}' does not exist.")
            if os.path.getsize(file_path) == 0:
                raise ValueError("Warning: The file is empty.")
            with open(file_path, mode='r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                self.records = []
                for row in reader:
                    cleaned_row = {k: v.strip() for k, v in row.items()}
                    self.records.append(cleaned_row)
                    
            print(f"Loaded {len(self.records)} records from {file_path} ")
            self.load_from_db()
        except FileNotFoundError as filenotfound_error:
            print(filenotfound_error)
        except ValueError as value_error:
            print(value_error)
        except Exception as e:
            print(f"Unexpected error occurred: {e}")

    def load_from_db(self):
        try:
            self.mycursor.execute("SELECT Application, Environment, Version, DeploymentDate, DeployedBy FROM deployments")
            rows = self.mycursor.fetchall()
            self.records = []
            for row in rows:
                self.records.append({
                    "Application": row[0],
                    "Environment": row[1],
                    "Version": row[2],
                    "DeploymentDate": row[3].strftime("%Y-%m-%d"),
                    "DeployedBy": row[4]
                })
            print(f"Loaded {len(self.records)} records from database.")
        except mysql.connector.Error as err:
            print(f"Database read error: {err}")

    def add_record(self, application, environment, version, deployment_date, deployed_by):
        if not all([application, environment, version, deployment_date, deployed_by]):
            print("Error: All fields must be provided to add a new record.")
            return
        for record in self.records:
            if (record["Application"].strip().lower() == application.strip().lower() and
                record["Environment"].strip().lower() == environment.strip().lower() and
                record["Version"].strip().lower() == version.strip().lower() and
                record["DeploymentDate"].strip().lower() == deployment_date.strip().lower() and
                record["DeployedBy"].strip().lower() == deployed_by.strip().lower()):
                print("Error: Duplicate record exists. No duplicates allowed!")
                return
        try:
            datetime.strptime(deployment_date, "%Y-%m-%d")
        except ValueError:
            print("Error: DeploymentDate must be in YYYY-MM-DD format.")
            return
        new_record = {
            "Application": application.strip(),
            "Environment": environment.strip(),
            "Version": version.strip(),
            "DeploymentDate": deployment_date.strip(),
            "DeployedBy": deployed_by.strip()
        }
        self.records.append(new_record)
        print(f"Added new deployment record for application '{application}'.")
        try:
            sql = """INSERT INTO deployments 
                     (Application, Environment, Version, DeploymentDate, DeployedBy)
                     VALUES (%s, %s, %s, %s, %s)"""
            val = (application, environment, version, deployment_date, deployed_by)
            self.mycursor.execute(sql, val)
            self.mydb.commit()
            print("Record inserted successfully into database.")
        except mysql.connector.Error as err:
            print(f"Database error: {err}")

    def delete_record(self, application=None, environment=None):
        if not application:
            print("Error: Application name must be provided.")
            return
        application = application.strip().lower()
        if environment:
            environment = environment.strip().lower()
            self.records = [
                record for record in self.records
                if not (record["Application"].strip().lower() == application and
                        record["Environment"].strip().lower() == environment)
            ]
        else:
            self.records = [
                record for record in self.records
                if record["Application"].strip().lower() != application
            ]
        try:
            if environment:
                sql = "DELETE FROM deployments WHERE LOWER(Application)=%s AND LOWER(Environment)=%s"
                val = (application, environment)
            else:
                sql = "DELETE FROM deployments WHERE LOWER(Application)=%s"
                val = (application,)
            self.mycursor.execute(sql, val)
            self.mydb.commit()
            print(f"Database deletion completed, {self.mycursor.rowcount} rows affected.")
        except mysql.connector.Error as err:
            print(f"Database error during deletion: {err}")

    def update_record(self, original_application, original_environment, original_version, **kwargs):
        found = False
        for record in self.records:
            if (record["Application"].strip().lower() == original_application.strip().lower() and
                record["Environment"].strip().lower() == original_environment.strip().lower() and
                record["Version"].strip().lower() == original_version.strip().lower()):
                found = True
                for key, value in kwargs.items():
                    if key in record and value:
                        if key == "DeploymentDate":
                            try:
                                datetime.strptime(value, "%Y-%m-%d")
                            except ValueError:
                                print("Error: DeploymentDate must be in YYYY-MM-DD format.")
                                value = None
                        if value:
                            record[key] = value.strip()
                            print(f"Updated '{key}' to '{value.strip()}'.")
                    else:
                        print(f"Skipped updating '{key}': invalid key or empty value.")
                print(f"Updated record for application '{original_application}' in environment '{original_environment}'.")
                try:
                    sql = """
                        UPDATE deployments 
                        SET Application = %s, Environment = %s, Version = %s, DeploymentDate = %s, DeployedBy = %s 
                        WHERE LOWER(Application) = %s AND LOWER(Environment) = %s AND Version = %s
                    """
                    val = (
                        record["Application"],
                        record["Environment"],
                        record["Version"],
                        record["DeploymentDate"],
                        record["DeployedBy"],
                        original_application.lower(),
                        original_environment.lower(),
                        original_version
                    )
                    self.mycursor.execute(sql, val)
                    self.mydb.commit()
                    print("Database updated successfully.")
                except mysql.connector.Error as err:
                    print(f"Database error during update: {err}")
                break
        if not found:
            print(f"Error: Record for application '{original_application}' in environment '{original_environment}' not found.")

    def display_records(self):
        if not self.records:
            print("No deployment records to display.")
            return
        print("\nDeployment Records:")
        print("Idx | Application | Environment | Version | DeploymentDate | DeployedBy")
        print("-" * 70)
        for i, record in enumerate(self.records, start=1):
            print(f"{i} | {record['Application']} | {record['Environment']} | {record['Version']} | {record['DeploymentDate']} | {record['DeployedBy']}")

    def save_records(self):
        if not self.records:
            print("No records to save.")
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"result_{timestamp}.csv"
        try:
            with open(filename, mode='w', newline='') as csvfile:
                fieldnames = ["Application", "Environment", "Version", "DeploymentDate", "DeployedBy"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for record in self.records:
                    writer.writerow(record)
            print(f"Records saved successfully to '{filename}'.")
        except Exception as e:
            print(f"Error saving records: {e}")

        import subprocess
        try:
            subprocess.run(["aws", "s3", "cp", filename, "s3://deployments-task-csvfiles-autoupload-talia"])
        except Exception as e:
               print(f"Error saving records: {e}")

    def start(self):
        while True:
            print("\n--- Deployment History Tracker Menu ---")
            print("1. Load records from CSV")
            print("2. Add a new record")
            print("3. Update a record")
            print("4. Delete a record")
            print("5. Display all records")
            print("6. Save records to new CSV")
            print("7. Exit")
            choice = input("Enter your choice (1-7): ")
            if choice == "1":
                path = input("Enter CSV file path: ")
                self.read_records(path)
            elif choice == "2":
                application = input("Application: ")
                environment = input("Environment: ")
                version = input("Version: ")
                date = input("DeploymentDate (YYYY-MM-DD): ")
                deployed_by = input("DeployedBy: ")
                self.add_record(application, environment, version, date, deployed_by)
            elif choice == "3":
                original_application = input("Original Application: ")
                original_environment = input("Original Environment: ")
                original_version = input("Original Version: ")
                print("Enter new values (leave blank to skip):")
                new_application = input("New Application: ")
                new_environment = input("New Environment: ")
                new_version = input("New Version: ")
                new_date = input("New DeploymentDate (YYYY-MM-DD): ")
                new_deployed_by = input("New DeployedBy: ")
                self.update_record(
                    original_application, original_environment, original_version,
                    Application=new_application,
                    Environment=new_environment,
                    Version=new_version,
                    DeploymentDate=new_date,
                    DeployedBy=new_deployed_by
                )
            elif choice == "4":
                app = input("Enter application name to delete: ")
                env = input("Enter environment (optional): ").strip()
                self.delete_record(app, env if env else None)
            elif choice == "5":
                self.display_records()
            elif choice == "6":
                self.save_records()
            elif choice == "7":
                print("Exiting... Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    tracker = DeploymentTracker()
    if len(sys.argv) > 1:
        tracker.read_records(sys.argv[1])
    tracker.start()
