import re
import sys

from datetime import datetime

from PyPDF2 import PdfReader


def open_encrypted_pdf(file_path, password):
    reader = PdfReader(file_path)

    if reader.is_encrypted:
        result = reader.decrypt(password)

        if result == 0:
            raise ValueError("Wrong password")

        return reader

    else:
        print("This PDF is not encrypted")
        return reader


def get_pdf_data(pdf):
    electricity_total_cost_re = re.compile(
        r"^Your electricity total \$(?P<electricity_total_cost>[0-9,\.]+)Your Supply Charges$"
    )
    electricity_total_amount_re = re.compile(
        r"^Delivery (?P<electricity_total_amount>[0-9\.]+) kWh \@.+$"
    )
    billing_period_re = re.compile(
        r"^Billing period: (?P<start_month>[A-Z][a-z]{2}) (?P<start_day>[0-9]{1,2})\, (?P<start_year>[0-9]{4}) to (?P<end_month>[A-Z][a-z]{2}) (?P<end_day>[0-9]{1,2})\, (?P<end_year>[0-9]{4})"
    )
    text = ""

    for page in pdf.pages:
        text += page.extract_text()

    text = text.split("\n")

    electricity_total_amount = None
    electricity_total_cost = None
    billing_period = None
    for line in text:
        if (electricity_total_amount_match := electricity_total_amount_re.match(line)) is not None:  # fmt: skip
            electricity_total_amount = int(
                float(
                    electricity_total_amount_match.groupdict().get(
                        "electricity_total_amount"
                    )
                )
            )

        if (electricity_total_cost_match := electricity_total_cost_re.match(line)) is not None:  # fmt: skip
            electricity_total_cost = float(
                electricity_total_cost_match.groupdict()
                .get("electricity_total_cost")
                .replace(",", "")
            )

        if (billing_period_match := billing_period_re.match(line)) is not None:  # fmt: skip
            billing_period_start = datetime.strptime(
                f"{billing_period_match.groupdict()['start_month']} {billing_period_match.groupdict()['start_day']} {billing_period_match.groupdict()['start_year']}",
                "%b %d %Y",
            )
            billing_period_end = datetime.strptime(
                f"{billing_period_match.groupdict()['end_month']} {billing_period_match.groupdict()['end_day']} {billing_period_match.groupdict()['end_year']}",
                "%b %d %Y",
            )

            billing_period = (billing_period_start, billing_period_end)

        if (
            electricity_total_cost is not None
            and electricity_total_amount is not None
            and billing_period is not None
        ):
            break

    kwh_cost = round(electricity_total_cost / electricity_total_amount, 4)
    # print("Electricity total cost: ", electricity_total_cost)
    # print("Electricity total amount: ", electricity_total_amount)
    # print("Cost per kWh: ", round(electricity_total_cost / electricity_total_amount, 4))

    return (billing_period, kwh_cost)


if __name__ == "__main__":
    filename = sys.argv[1]
    password = sys.argv[2]

    pdf = open_encrypted_pdf(filename, password)
    print(get_pdf_data(pdf))
