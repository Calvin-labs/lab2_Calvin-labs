# Grade Evaluator

Python + shell tool that evaluates course grades from a CSV file and archives old grade files.

## Files

| File | Purpose |
|------|---------|
| `grade-evaluator.py` | Reads a grades CSV, validates it, computes the final grade, GPA, Pass/Fail and resubmission options |
| `organizer.sh` | Archives `grades.csv` with a timestamp, creates a new empty `grades.csv`, logs to `organizer.log` |
| `grades.csv` | Sample input data |
| `Readme.md` | This file |

## CSV format

```
assignment,group,score,weight
Quiz,Formative,85,20
```

- `group`: `Formative` or `Summative`
- `score`: 0 to 100
- `weight`: total must be 100 (Formative = 60, Summative = 40)

## Usage

```bash
python3 grade-evaluator.py
```

Enter the CSV file name when prompted (e.g. `grades.csv`).

```bash
chmod +x organizer.sh
./organizer.sh
```

## Logic

- Category percentage = weighted points earned / category weight x 100
- Final grade = sum of (score x weight / 100), out of 100
- GPA = final grade / 100 x 5.0
- PASSED only if BOTH Formative and Summative are >= 50%, otherwise FAILED
- Failed formatives (score < 50) are listed; the one(s) with the highest weight are the resubmission targets, including ties

## Validation and edge cases

Clear error messages, no crashes, for:

- missing file, empty file, missing header or columns, header-only file
- empty rows (skipped)
- non-numeric score/weight, invalid group, empty assignment name
- scores outside 0-100
- weights not summing to 100, or not split 60 Formative / 40 Summative

## organizer.sh

1. Checks `grades.csv` exists
2. Moves it to `archive/grades_YYYYMMDD-HHMMSS.csv`
3. Creates a new, empty `grades.csv` ready for the next batch
4. Appends the timestamp, original filename and archived filename to `organizer.log` (the log accumulates every run)

Creates the `archive` directory first if it does not exist.

Note: after running `organizer.sh`, `grades.csv` is empty. Restore your data before running `grade-evaluator.py` again.
