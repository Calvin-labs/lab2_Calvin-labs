import csv
import sys
import os

VALID_GROUPS = ("Formative", "Summative")
EXPECTED_WEIGHTS = {"Formative": 60.0, "Summative": 40.0}
EXPECTED_TOTAL = 100.0
PASS_MARK = 50.0
REQUIRED_COLUMNS = ["assignment", "group", "score", "weight"]


def load_csv_data():
    """
    Prompts the user for a filename, checks if it exists,
    and extracts all fields into a list of dictionaries.
    Exits with a clear message on a missing/empty file, missing columns,
    or invalid data. Empty rows are skipped.
    """
    filename = input("Enter the name of the CSV file to process (e.g., grades.csv): ").strip()
    if filename == "":
        filename = "grades.csv"

    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)

    if os.path.getsize(filename) == 0:
        print(f"Error: The file '{filename}' is empty.")
        sys.exit(1)

    assignments = []
    errors = []

    try:
        with open(filename, mode="r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                print(f"Error: The file '{filename}' has no header row.")
                sys.exit(1)

            headers = [h.strip().lower() for h in reader.fieldnames if h is not None]
            missing = [c for c in REQUIRED_COLUMNS if c not in headers]
            if missing:
                print(f"Error: Missing required column(s): {', '.join(missing)}")
                print(f"Expected columns: {', '.join(REQUIRED_COLUMNS)}")
                sys.exit(1)

            for line_no, raw in enumerate(reader, start=2):
                row = {}
                for key, value in raw.items():
                    if key is not None:
                        row[key.strip().lower()] = (value or "").strip()

                # Skip completely empty rows
                if all(value == "" for value in row.values()):
                    continue

                name = row.get("assignment", "")
                group = row.get("group", "").title()

                if name == "":
                    errors.append(f"Row {line_no}: assignment name is empty.")
                    continue
                if group not in VALID_GROUPS:
                    errors.append(f"Row {line_no} ({name}): group must be 'Formative' or 'Summative', got '{row.get('group', '')}'.")
                    continue

                try:
                    score = float(row.get("score", ""))
                    weight = float(row.get("weight", ""))
                except ValueError:
                    errors.append(f"Row {line_no} ({name}): score and weight must be numbers "
                                  f"(got score='{row.get('score', '')}', weight='{row.get('weight', '')}').")
                    continue

                if score != score or weight != weight or abs(score) == float("inf") or abs(weight) == float("inf"):
                    errors.append(f"Row {line_no} ({name}): score and weight must be finite numbers.")
                    continue

                assignments.append({
                    "assignment": name,
                    "group": group,
                    "score": score,
                    "weight": weight,
                })
    except (OSError, UnicodeDecodeError, csv.Error) as e:
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)

    if errors:
        print("Error: the CSV contains invalid data:")
        for message in errors:
            print(f"  - {message}")
        sys.exit(1)

    if not assignments:
        print(f"Error: '{filename}' has a header but no assignment rows.")
        sys.exit(1)

    return assignments


def validate_data(data):
    """Returns a list of validation error messages (empty list = valid)."""
    errors = []

    # a) Scores must be percentages between 0 and 100
    for item in data:
        if item["score"] < 0 or item["score"] > 100:
            errors.append(f"Score for '{item['assignment']}' is {item['score']:g}; it must be between 0 and 100.")

    # Weights must be positive
    for item in data:
        if item["weight"] <= 0:
            errors.append(f"Weight for '{item['assignment']}' is {item['weight']:g}; it must be greater than 0.")

    # b) Total = 100, Formative = 60, Summative = 40
    totals = {"Formative": 0.0, "Summative": 0.0}
    for item in data:
        totals[item["group"]] += item["weight"]
    total_weight = totals["Formative"] + totals["Summative"]

    if abs(total_weight - EXPECTED_TOTAL) > 0.001:
        errors.append(f"Total weight is {total_weight:g}; it must be exactly 100.")
    for group in VALID_GROUPS:
        if abs(totals[group] - EXPECTED_WEIGHTS[group]) > 0.001:
            errors.append(f"{group} weight is {totals[group]:g}; it must be exactly {EXPECTED_WEIGHTS[group]:g}.")

    return errors


def evaluate_grades(data):
    """
    'data' is a list of dictionaries containing the assignment records.
    """
    print("\n--- Processing Grades ---")

    errors = validate_data(data)
    if errors:
        print("Validation failed:")
        for message in errors:
            print(f"  - {message}")
        sys.exit(1)

    # c) Weighted points per category and overall
    earned = {"Formative": 0.0, "Summative": 0.0}
    possible = {"Formative": 0.0, "Summative": 0.0}
    for item in data:
        earned[item["group"]] += item["score"] * item["weight"] / 100
        possible[item["group"]] += item["weight"]

    final_grade = earned["Formative"] + earned["Summative"]
    gpa = final_grade / 100 * 5.0

    print("\nAssignment breakdown:")
    for item in data:
        print(f"  {item['assignment']:<40} {item['group']:<10} score {item['score']:>6.2f}  weight {item['weight']:>5.1f}")

    # d) Pass/Fail: >= 50% in BOTH categories
    percent = {}
    for group in VALID_GROUPS:
        percent[group] = earned[group] / possible[group] * 100

    print("\nCategory results:")
    for group in VALID_GROUPS:
        status = "PASS" if percent[group] >= PASS_MARK else "FAIL"
        print(f"  {group:<10} {earned[group]:>6.2f} / {possible[group]:g}  ({percent[group]:.2f}%)  {status}")

    print(f"\nFinal Grade: {final_grade:.2f} / 100")
    print(f"GPA: {gpa:.2f} / 5.0")

    passed = percent["Formative"] >= PASS_MARK and percent["Summative"] >= PASS_MARK

    # e) Failed formative assignments (< 50%) and highest-weight resubmission targets
    failed_formatives = [i for i in data if i["group"] == "Formative" and i["score"] < PASS_MARK]
    resubmit = []
    if failed_formatives:
        highest = failed_formatives[0]["weight"]
        for item in failed_formatives:
            if item["weight"] > highest:
                highest = item["weight"]
        for item in failed_formatives:
            if item["weight"] == highest:
                resubmit.append(item)

    # f) Final decision and resubmission options
    print("\n=== FINAL DECISION ===")
    if passed:
        print("PASSED")
    else:
        print("FAILED")
        for group in VALID_GROUPS:
            if percent[group] < PASS_MARK:
                print(f"  Reason: {group} category is below 50% ({percent[group]:.2f}%).")

    if failed_formatives:
        print("\nFailed formative assignments (< 50%):")
        for item in failed_formatives:
            print(f"  - {item['assignment']} (score {item['score']:g}, weight {item['weight']:g})")
        print("\nEligible for resubmission (highest weight among failed formatives):")
        for item in resubmit:
            print(f"  -> {item['assignment']} (weight {item['weight']:g})")
    else:
        print("\nNo failed formative assignments. No resubmission needed.")


if __name__ == "__main__":
    # 1. Load the data
    course_data = load_csv_data()

    # 2. Process the features
    evaluate_grades(course_data)
