import pandas as pd


class FileComparator:

    @staticmethod
    def load_file(file):

        filename = file.name.lower()

        if filename.endswith(".csv"):
            return pd.read_csv(file)

        elif filename.endswith(".xlsx"):
            return pd.read_excel(file)

        elif filename.endswith(".json"):
            return pd.read_json(file)

        elif filename.endswith(".txt"):
            return pd.read_csv(file, sep=None, engine="python")

        else:
            raise ValueError("Unsupported file format")

    @staticmethod
    def compare(df1, df2):

        df1 = df1.reset_index(drop=True)
        df2 = df2.reset_index(drop=True)

        total_rows = max(len(df1), len(df2))
        common_rows = min(len(df1), len(df2))

        matched_rows = 0
        modified_rows = 0

        differences = []

        added_rows = max(len(df2) - len(df1), 0)
        removed_rows = max(len(df1) - len(df2), 0)

        added_columns = list(
            set(df2.columns) - set(df1.columns)
        )

        removed_columns = list(
            set(df1.columns) - set(df2.columns)
        )

        all_columns = sorted(
            list(set(df1.columns).union(set(df2.columns)))
        )

        def safe_get(df, row, col):

            if col not in df.columns:
                return "COLUMN_MISSING"

            try:
                value = df.at[row, col]

                if pd.isna(value):
                    return ""

                return str(value)

            except Exception:
                return ""

        for row in range(common_rows):

            row_match = True

            for col in all_columns:

                old_value = safe_get(df1, row, col)
                new_value = safe_get(df2, row, col)

                if old_value != new_value:

                    row_match = False

                    differences.append({
                        "Row Number": row + 1,
                        "Column Name": col,
                        "Old Value": old_value,
                        "New Value": new_value,
                        "Status": "Modified"
                    })

            if row_match:
                matched_rows += 1
            else:
                modified_rows += 1

        match_percentage = round(
            (matched_rows / total_rows) * 100,
            2
        ) if total_rows > 0 else 0

        return {
            "totalRows": total_rows,
            "matchedRows": matched_rows,
            "modifiedRows": modified_rows,
            "addedRows": added_rows,
            "removedRows": removed_rows,
            "addedColumns": added_columns,
            "removedColumns": removed_columns,
            "matchPercentage": match_percentage,
            "differences": differences
        }