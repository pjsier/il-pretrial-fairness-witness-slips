import csv
import sys
from datetime import datetime

import requests

AJAX_URL = "https://my.ilga.gov/Hearing/AjaxRetrieveHearingLegislationWitnessSlips"
POSITIONS = ["PROP", "OPP", "NOPOS"]
OUTPUT_FIELDS = [
    "WitnessSlipId",
    "FirmBusinessOrAgency",
    "Representation",
    "PositionTypeDescription",
    "TestimonyDescription",
    "timestamp",
]
PAGE_SIZE = 1000


def request_slips(hearing_id, chamber, pos, page=1, size=PAGE_SIZE):
    return requests.post(
        AJAX_URL,
        headers={"X-Requested-With": "XMLHttpRequest"},
        params={
            "hearingid": hearing_id,
            "chamber": chamber,
            "positiontypecode": pos,
            "legislationdocumentid": "0",
        },
        data={"page": page, "size": PAGE_SIZE},
    )


def slips_for_position(hearing_id, chamber, pos):
    slips = []
    total_slips = 1
    page = 1

    while len(slips) < total_slips:
        print(
            f"Requesting page {page}: {hearing_id}, {chamber}, {pos}", file=sys.stderr
        )
        res = request_slips(hearing_id, chamber, pos)
        data = res.json()
        slips.extend(data["data"])
        total_slips = data["total"]
        page += 1
    return slips


if __name__ == "__main__":
    hearing_id = sys.argv[1]
    # chamber = sys.argv[2]
    chamber = "S"
    slips = []

    for pos in POSITIONS:
        slips.extend(slips_for_position(hearing_id, chamber, pos))

    output_slips = []
    for slip in slips:
        output_slips.append({k: slip.get(k) for k in OUTPUT_FIELDS})
    output_slips[-1]["timestamp"] = datetime.utcnow().isoformat()[:-7]

    writer = csv.DictWriter(sys.stdout, fieldnames=OUTPUT_FIELDS)
    writer.writeheader()
    writer.writerows(output_slips)
