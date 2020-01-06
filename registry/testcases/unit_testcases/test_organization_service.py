import unittest
from unittest.mock import patch, Mock
from uuid import uuid4

from sqlalchemy import func

from registry.constants import OrganizationStatus
from registry.domain.services.organization_service import OrganizationService
from registry.domain.models.organization import Organization as DomainOrganization
from registry.domain.models.group import Group as DomainGroup
from registry.infrastructure.models.models import Organization, OrganizationReviewWorkflow, OrganizationHistory, Group
from registry.infrastructure.repositories.organization_repository import OrganizationRepository


class TestOrganizationService(unittest.TestCase):

    def setUp(self):
        self.org_repo = OrganizationRepository()

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock(return_value="Q3E12")))
    def test_on_boarding(self, mock_boto, mock_ipfs):
        org_service = OrganizationService()
        username = "dummy@snet.io"
        payload = {
            "org_id": "dummy_is_dummy",
            "org_uuid": "",
            "org_name": "dummy_org",
            "org_type": "individual",
            "metadata_ipfs_hash": "",
            "description": "",
            "short_description": "",
            "url": "https://dummy.dummy",
            "contacts": [],
            "assets": {},
            "addresses": [
                {
                    "address_type": "headquater_address",
                    "street_address": "F102",
                    "apartment": "ABC Apartment",
                    "city": "TestCity",
                    "pincode": 123456,
                    "country": "TestCountry"
                },
                {
                    "address_type": "mailing_address",
                    "street_address": "F102",
                    "apartment": "ABC Apartment",
                    "city": "TestCity",
                    "pincode": 123456,
                    "country": "TestCountry"
                }
            ]
        }
        response_org = org_service.add_organization_draft(payload, username)
        test_org_uuid = response_org["org_uuid"]
        test_org_id = response_org["org_id"]
        payload["org_uuid"] = test_org_uuid
        org_service.submit_org_for_approval(payload, username)
        self.org_repo.approve_org(test_org_uuid, username)

        payload = {
            "org_id": test_org_id,
            "org_uuid": test_org_uuid,
            "org_name": "dummy_org",
            "org_type": "individual",
            "metadata_ipfs_hash": "",
            "description": "that is the dummy org for testcases",
            "short_description": "that is the short description",
            "url": "https://dummy.dummy",
            "contacts": [],
            "assets": {
                "hero_image": {
                    "raw": "/9j/4AAQSkZJRgABAQAAAQABAAD//gA7Q1JFQVRPUjogZ2QtanBlZyB2MS4wICh1c2luZyBJSkcgSlBFRyB2NjIpLCBxdWFsaXR5ID0gOTUK/9sAQwACAQEBAQECAQEBAgICAgIEAwICAgIFBAQDBAYFBgYGBQYGBgcJCAYHCQcGBggLCAkKCgoKCgYICwwLCgwJCgoK/9sAQwECAgICAgIFAwMFCgcGBwoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoK/8AAEQgAsADcAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQYHCAkKC//EALUQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+v/EAB8BAAMBAQEBAQEBAQEAAAAAAAABAgMEBQYHCAkKC//EALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXETIjKBCBRCkaGxwQkjM1LwFWJy0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/aAAwDAQACEQMRAD8A8+8OWAmuHknJPyjBxnnJrfOnSzfuI4mLD+Ijn8fzpvh/TJY08548DJIIGTgfzrds7VJHaRoiDgdflBHGO3sKyNCvpWhQpvIKBnbLMBjJ9a3NKsjZ3jxyL82w4IJAX681Clk5iSW0VgEIMhAHGSR+PU1uWOm3U+pJPNG6q0BBOeMdvpx+efahdAJ9KsIZ0M1xG7jPzkEevv7c/jVuCxSS9DW7hkMnKkYO085/pmtbQNBkgUlE5CqSmcEDJ56dOK3G0GBbiOaKJXxyVK556dqYjPFrJDbedg4JwoY8t2FZht9RbUhDOuV3DzMjAz/9b1PtXXPoiyRxbY33rLmP5c5Yj/69WbTw6DdtGylmVchPQY/+uKBJGDpWlpZqWtoshF2/Mfvc8/rU9ppV0YZpHA3Bz+6IyVx2/Kukm0d2CwwQh5Oi+g4yc/57Vrad4YFio+1KMyOdvy8fjQFjy3WdEuYNUW68oKG+UoVyCcZ4H5/lVnwv4Ym1EpDLbYBAbanHQgjPcniu/wDFXhdbqAvHFGFLbVxyCe5/Co/DegX9hZTsqBrkKdgVchjkgYx0oGtTkr7SIbfUZo4mRSB6fdrK1qwjDx2tqFeRdp4XkZ712d7oNzHK97dqzSZ3MP7xz9KS38OtMUnvY1SVW2gIpIIPOPwxUPcDml0YSne/l9CCSv8AT+dRQaXMIg6RkIn3S4xkZNddrfh/7QgSwyTIAUGPu46n+VSt4ZQJGrBt20DGR1/z/KrA4u48IJcSb5pAeOI1IB9uPzqte+GmhsGhNqThifmOTXolp4ThltFuFLBYg33s5Bzjj9ahuPDZuYftY3IME8jPTj+lAjyR/DrPObqSOSV2wMEY2jtWL4h8PPdzGBwzHHGeQMkZ/DFev3XhefBV1IVxkbhxjjJH5/rWdrfgtd0dwtsPlJ5C8hSvSgdz59+KHhSKCKHdZiZUcKmWwBk5zxV+x8JRnT7VPs7CLKnAPCkDk/zrsfH/AISFzEkVujArMpG5eR83t9a0tc0f+xNAt4YtODvvRZyuTu4we3HH41K3GcNfeE5YIiuDtJByw6LnP/16SDw9b24AAGABjBB7+3fg13t1oyXsrRx2+VjUDDHnBqu/h8sJIZoFAZSQ6+xzmqJORurSWSLKFT68e1clcaBic3BcB4zkEL1znj+deoXGmxtHIhVhEFAUrjk+o/SuX8U6LLask9tvyQFlVRkLj19OtAjg9e0jzrdcvtkVNvDYCknn61nJYPFlJQ7HPB46fjXcazocMulp5iCNh8xZDyCeazLfQ7R4VaTzs47img1O40Xw3cW6Rfabc42kfL2/A/lWodGebY5tid7nauOOP8k/hWzpejlws8srABiOD1x2/Wt3SNCiEhEySfd4BXikWc/p3he5gjS2MSDzZOTIuAAP5/1rpbbw1ZxY8wA+WBwO4PH4c10uneHIbow3DxO5L/dwSoGMf41raf4SaS+RzY7IyQF7bgOpJ7UAUtH0xPLSGOPaQuHAHUVvWHhO2TYwsyQeinB5z/8ArretfDP2jcyx4U/cz1z9BXQWPhKaMLIItseOWwCcnil1EcdP4SVQqraZaNgzxqu3IHuPY8VsWfgizjnj1KSJWPkeWqoOo9T+Rrt9D0QwW3n3BDEZChgMEdAcmtCy8OaZcu0n2fY5bAKjjrzTA4a18BwLI7W1uQDyRjv9Bz0raHhJLm1EcSHEZ7pg+/Wu7ttBsrAeXbwAEgYJ65PHWmvok8wZmUbQeVXjAFAHmWveFkOpLbWtokZClVeVSVPfpg9D/wDrpdD8GuLd3hUyPFK25WGORivRpvDVizl2uW8w8tk5IHoP51Pp3htFjmABELOXwV65+vXpQB5Fqfhva8qSx/vUYIuAOmMn8zVG08PlrtbNhkHhiDg546H8DXq3iPwpEJo32Mf3oyuRzn1P+etUW8KLbSiVLPbKGG35uOO2aVtRnEyeCbSOOKCFHEatnzFPO7nOabJ8OJLiVXiZgg5w4+/3zXoNppDTK9tb2RTCbmz0z1rVXSY0CRPbKMpgDkgc9qYjzex8Bx22biDZIArKR2Jz9evB59qqN4MmZCZIDhzgqqjAGa9asvDlsIxG0JYZ4Lp2OTwP89KqzeHogGl8lwpH8Q4PPFAmzyK78DzmZZZoo9nRZGU5x3GO3TFRX3gR5HMUioyScJ9OOceteqav4d+0stwiIAvDZ/hx1Pvn+lYes2SRy+ZHgEMNzqnC8UAj5+8c+BJEnRGQhfM5Vhyeen547+tO17wyLjSRBJbnJIaIKo+9kj+n+elep6r4Ze/njvU2sVlVkjkbA+9gn2x1/CqvizRFtLJI/s4RXlUA4HrxyeeRSsM8u/4Ri4lRy0YVgo2MepIHt+NQaj4ZktYFhaLLsDtYDBQEdvavUbPwvOsPmbCGI5z1UcHpjrVTVfCe6VnznjEjEcAUxWPJbrwqqQJGIsKeCATnH+f5VzPi3SZbG0E9kg+V1XBGdw6f5+te0ar4ct4fkEB/vKdvA4/lXG+JNNs4blNOubTZHKNqlsgH/A9KYrnkOr+HVu7cS+S0TrgOgOef8KpRaa9unlS2BkI/iIHp7n1zXomqeF49MDtl2V2wu/nnIwOcVnR6M8IMQtHcBjg+lC0A6bSbB5EC+ahkZTtyuOv0/Cul0nQZbVwzOSXXAJ46/jxVrSPDsSNFDMcBgNuBxXY6L4ejEbQ7A+OhLYPXGPpSLG+GtLQ26W4VnDnkjnHTv/nrXS6dojTuymIYRj9PpT/D+gJaDzBCkSqcfXjrn0roNBsLme6ZnBdSDwDwcccH/P4UAS6T4fTerzRMPl7Hr+dbdpo8jNhYip2nIB6Ve0yFI3DeXgRgde4rbsVt5pMRwvkqcqR1oEY1hpUj5gWAMi5B2ZHf/IrXttGDW/lCInJyrY5FWxYzRoLq2fCp95UTBP4VbjDJZANuLHg5U4I9iOnWgEVodIMZiiXseT+tXJrOOIhHizuPL7OoPartrZ+Yq7lPOMMVyDnv/OrNxH5a7I13sARkqAMdsd6AOZXw9DLLK9w+0SvtUOcEj29qu2WhTNbGDhtiEEKMgrnpnGM96vPpH2x2DFAAcgPn0x7YrV0ezjs4Hj3ZEfykjpjHHPegGcFrNi0t6ltbQb9vKZ6Hr0J/GoxpdzOu2aEK69vLx8vTg102p6bGb9bq3G1wASD09zinT2SyTJdLOgUj5weu314pdQMfTvDECyK6QkB1O75RwTxzVm+0Y25RUkC7RkEpjAxW1p2nrb3DOiMdyEhTkjr19qdNpi3EuHJbHzbQOBTEc5PbiGbzQHbbhSBzzjvn/P51YktotRCjYysG4XHTHTmup0TStGhvGn1aOR7eKNmeKIfNJheFGPf+dYfhODV9RsJb/wASabDaXEtwzQ28R5ji6qG9SM4PTOBxU8y5uUrlbjzHM3mj3Edw2/nJ+RNp659fzrC1Lw6y5N0rFnk4Cj7g/rXpOraYm0mJtxBz0/pWKbCKacrnBDkZ7Eg9BVErY80vdKjiuBAyE7ORnrjjgfnVTxj4fldFhliLRo4YY/h7/wAhXZaxoSS6qVkDYjcbTjBGKr61bTvbSRyRAKEG3J569DQM5CKweWMNCSRswfm6Y6ZrN1jTMxeTLIqk5zuGcj0/WuytNNhFhkty33iOzYqpJpqXDGOXKKVyMr/9agRwGreH38hZ2IIjGF2ZAx/n+lcH438PW17/AKRcqEdBjaO6568fnXsms6FEXacSj72AxPQY/TtXGeKPCzrcs8UhMbKDlsYDZ6d+1AI8f1qN3i+0ysG2HbypwSOhrJe0lOFa2IYDDAZ4PWvQ9d0axtiYpF4U5KHHU8Zx6D+prnruW3jnKxnI75B6/lTQj0PT9OgkMb/Zt7jkAkH866bQLUJKC6RqI/8AWgEk5z2rO8O2stq6si5xgb2HPIzjp9a6WG3QR+YAVHdtuPxGPwFIsuyvbRSRxR2xVpSd5Ze4Fbuny20fliC43RRjlfK5Vh1HH1rBvY1WVIDuG9ARgZ4zjoP8/wAq6HwVobyQB5QSC5Iwv8qANvSmluQxQEpv+YkEHOP6/wBK2NO82G4KNcfLgbdvYdxnt1qfT7COSQCNFACkMMd6tT6DDLCQkHU9e2f69KBal6JEkYJGzMuPugf16VYuHiuViRbZyQ2N+3GGPrTdLjbTrdbNURjgbFPH4Z/L86u2doLa9DSybTJghfUnj8aAH6cnlq0ciAYB2gHrzTi3l7wFLgjkBf1q99ikhVl8qUsT1IBGB25+tKdNDn7OLfgHnA6j0+tAWMy2isrqQyvbkyFSAueMdfx6Vnaz4r0Pwjol34j8Wa5Z6VpdnGz3d/qF2sMFugPLu7kKg9yR1rW1C3NvcMEjI4yyhen0qj+0b+y5+yP8ffA9n4F+PHgw6zDEhkST+0bmMwyEZ80CGRRuzwDjIBwDUykoq514KnhKmKjHFOSp395xSlK3km4q/q9N9dj5D+MP/Bcr9gv4aa02k+H/ABLrPjKVD5csvhjS1a3Rh1xNcPEHH+1HuHvXLWH/AAcA/se6uQl/8NvH1qQCBJDZWM4X6gXQI/KuX/bk/wCCFzpog8S/sKz3Mt4ny/8ACH+IoTdWt0irwY5rhmlic4HcoSRwuS1fA/hL/gm5+238Ydfk8PWH7LTaDcwnbNf3GpfZoN2WGQCX3jKEfICOK8+WJrKWp/SfDnD/AIAZjk6nWrVI1Eve9rNwlf8A7cThbtp+J+mOrf8ABfr9hTw3p73MGm+PrxggxbRaBAHJGeMvcqv61j/AP/gqp+0t/wAFDviq3w+/Y0+AsfhLwpprK3iz4jeLJRdvp9u2flht0CxfamAIjRnlBPzMoVWNfPXwO/4Npfjt4s1a2139pD47aHo+grIDcWHhgT3d9Ko+8gaeKKOInoHxJj+6a/Vj4D/s1/B39mD4V6b8Hfgx4Tg0XQ9NjIihQkyTyEDfPM5GZJWIyWY54HQAAdNKVWqrt6H53xfV8NMmcqGRUJVqnSc5uUY+aVoqXkmmur2s9oeJIllid43MjKAzSKASPXgev05NJbXQup5MQuv7zG7O4857jkf/AF604NEsZbsXKQROduM5zn86nbSxE2Y7aMKcbsKAc44NdJ+SPcxdV+S1EqSFWYHejJ7evasfTZVmlZ1gYmNSAFAPOODXTX2iSzIWgU7mX5l5AHv/APWrE0zSG0xJZ1jj8xlzjdkZz1+lAJmNfRSSyrI1oGkJIJZsAkfTpzVPxDpVxcWrqsQ3FQZAT2+pNdBHExxKFJYDj9R+FZniK7nubOWKF17Jt2fdBPU4PsaBnJ22nTupjnYhRz8oxUFxpds6DiRncZ5Y/KMdq6S2s41YRhD3OCMD1/OopbD7O4eQchvvEZ+n86AucTfQXsZKyHO7IG7v9Of85rjdd05ry4Bv51jkjcmIZIJOcdK9U1myhmwCoLKeGxjqPSuU1XwtCG803GXQ7idxP4frQJM8v1Dw2r5BuGHUuMAHHZenTOayf7BsLdjF5aHB6lc5/Pp9K7fxXAijKxSHBITauC2OvP8AnOK4u8vLg3DeVGyDjKNNgg478HmgDt/CQS+DMyggOOHHy4A9vwrr49qW4ZlXb/EQvToMAfnXKeFLFAR5M4QFv4RxXX6QMKbeSTLOfmxgDHH+fxptjsOltvtDwBQ6gnYD0Ars/DEPl+WuwBScqAckjHrXP29kL51tLeMK45DenSur8NWskKeRknjGSMnP+eaQzasrmOK+2I4C4ywfvWvb3Nw0oCkCLb90jPNUk04TPHM7Bdq9QcE1p20ZhlWKAgjcQ7EZ/KgAnhlISRoFBBByR0OferFpYXUt0ksvVMsue30q6Le22g+YC2MYIJ5p7SEFTszgYJAP+RQLqWLEyTMzSDdu+6c5JonneBwY1fJyCCMHrSwxOIVwRzyFz/8AXqwLWecEDdmIfeAAFIZl3lvBekyPGdw4HBz+dfIPxd+In7Yut/E3U/BXw3+IM2maGmpv50kPkCe2VgNqxnyWd1BZRww2kE5wVB+1IYhPILSFlRuS5UDGMYNeAeLPAPiq3+JtvdeEr9beSzuJJtXg2GVJYNwACRsdqSFWUGYqxwDj1HFjYzlGNnY9HLatKlUk5xvp1V/zO8sPH+neEvCdtfanrc9ze22iCRY7qZkmupCoAVzJ8wJJU44Oc+4rnrr9o3wj4R+BOv8Axl16/j0q08P2bW+pR3gSe5hywRo1XudzqiZ+8WHXvxv7YMHxF0vw9b/EaK/sLC3j0ye8vtREePOWLLNAjr8iuYlYBW+9g4Py4P5M/wDBSr9trXviR46sfgj4C8RzweHYLGDU/EdtbzOEuryfMqq5blwkUikBvuscYzGDXI+ZH2nBHC0+L+IaOAT5YN3m+0E/et5vZX0u1fQ+q/Ef/BeX4qwa/PB8PPgz4eTQVCiwj1R53uXA/jeRJFXJ5O0Lxnv39R/Zq/4Lm/AT4i+J7bwH+0hoLfD67vpPLs9fku/tGlXEh/gkk2hrZs/38rjJLADNfjZ4y+KsnhXwrNJZANcyXbQxszHCZLEHA/2a47RviNqfiO8/s6/nt5BOAkcc0alGYdAd2cgn1zzz1ArGhXxUfevof05xp4a+F9HDxy+jh/Z12laUZS5lfa92027dU9z+qqxVZoY7/TbtLi3njV4Z43DI6MMgqwOCpGDkdc1bRbuSJUdwqcMowc8H1r8KP+CXv/BZz4l/sP8AiDTvgZ+0N9u174WX10YbBpnL3nh4lsMkLMfmRM/NCxwfvKVJYH91PCHi/wAH/FDwjp3xC+H/AIjttZ0LV7YXGm6jZy7o5o27g9QeoIOCCCCAQRXs0a0asbo/kLiThfH8OYp06qvC9lK1td7SXSVtbbNaxbWo95biK2bZIgV8gnPzdetczcXEVvPLbSqfvEh+gIz6V08qRI27ZkKxAA9ayLy0jvHkiMY3sOW6celbHzVjAilMuf35yzfJj2J/Osu8s7s2ZtmuHAJywK4zz1JrabSzazSIxLZB2jklTn8qh1CJ/LWKVC0hAOVH4HofSgDF0nT5ot7zOeDtGFJI9M/hmrBt2ktywdS3TGOMdK07M2NtC0U7MA/A59qyYg0epeXAvyPyzZ4AoC1zI1SBopmTbnHYjOMYz271zHiUXMEjyWKFcqAeOnXqOeen5V2+tS2wmR4i7Hed7J0HHf06Cuf8RwxvaCHzBDwdr9cZxTFseY+ILqO6jCw2+6aNGjLZIUcZ/wA8dq5200e7mi3SQucNgFiBkDvxXbajpcJ3Ryxn5s5bJ2E9Aev0rJGnGL5HkZTnkYpAWfDdkWiDMUbaflBY89813Gi2lv5irFFuBGWYNg5/KuO8GGaSVZfMIC8A7jx/nNdrohW4uv3aYUNwSvOB1/Wgo3bKwHmJ9nh2kYySeTk/57V1GiWTJbecwVSGJ3bv6Vj2ECG5BU4PBbnsPx/ziujsIlitEhES4bg89KAL+n2qyxDIzvHGSKv21pCZiqMh24yuc4470WcP+hiRYhy2MGtNLeCCPzIIyM5+93/GgCK1s2JV0XcikbQv+f8AOK0bGxtYxI+3cSfXJ/z/AIUmkxxyKsgHPRgB7Y/GrsAcwBwdzMxJcL0HQUAVEt4jKq7HPQDYeBVuLytkuzG5QQd/Ofp61EJpftBYLtGOCV6n3oM222aaJQxySSCO3c0gHWdkrsStsy56MvGP1ryD47aXrd38QRqGkeOrPQFtrKNJGljGZ8NvYEnqMDGO+OAeK9ghvJFCR73GG+Ycc/5zXk/7VvhXVb/SV8U29lFLa2UURIbO6SXzCFG0Kc9RncMdB61jXTdLQ2w7Sqanyj/wWJ+OPgD4XfsZapL4l8U3E2rQxW8WjaTFOBbX91uywlX+JCu75Q38JwDivw/8ODVPE11ca5dzNPeahc/vJX6u/wAzSOx9MkH3r9bP+Cu/wq174zfB668M6kz2+lWuiNqWns8e1kv7eOSQB8LhtyhlJGB97HJFfjh4fbXL6wZ31pNNsLdd0sjyEZ74AAyx6flXmy95M/ovwSx1HLsVWnyuTaT0tpa+rk7JKzd29jY8e2xtYZF1RXVPOAjaNQ3QHG4fQ9q5CXTdMvJT/Zd8ob+EA7f0q3qfxTudL1aSDRYft1p5Ucey9RsNhfmb1GTnriret2WmxWMOpato62Mtwx2pHIWC4GeRgFOvTk8dKcYygkmfrmbZ1kXEdarKjJN0/iupWWrV1UV4tPpoafh/xIniOyPw1+IrDybpkSy1Z0/eWsy/6pmP8QH3eedrMM4xj7i/4I5/8FVPEX7F3xcsP2dfjxr1zZ+BtY1IWep/2ru8jTJydi3sbHO0AhRIR8rJkkblBr4I0PVLL7dDY6pNBdWEzBJMygvGp7qThuOvPp+Nfop+wt/wSf8AC37Wnh3U/FnxJ+KVza2kDxTPZWNmrTyx+WrFvMkyiBiTk7CeaUVKFVci8/6/VH59xHXyX+xatTNKy5H+7u4ucpXUpQWnWLTdOpfTVS0sj9w7+zkm/wBLsp4pI3VXRkbhwe4IyCKpT2cCRuVY5YjvgrmovhRHpNj8K/D2j+HG87T9O0WCytnL7iVgQQjJ7/cPNPmlBcxxhkJcAPjqc9MV7Cd1c/lSfKptLYotEvml2LkKCGyvfis69gkNwrxodv8ADkniuguoEa8baXZipDAnofTioL+2PkhjENrAYAHA/wA80yTnUsrqSPY0AGG+cvyMd6rahpjQNut0XaGAJJ5I/wD1V1xs4Psa3JBUrgE9/wDGsi9t1eLzGl3xk/cbA+v9aBnLXmn2MsjIs2zn5cMOlYuv2LywzGzkA2DADL1xz9AK3vELWHn/ALuFt23Ckc47nGawrl2kzaRMdjgMp7jvQS7nF6to9xNp6s1zudiTtL8A5/TpWTd6K0ly7DJ6ciQEdB6muv1EAW2y1jwEyCY2AG7rxXNXnmC7kEcb4DdVY81SQrsoeG45mVYfOVSXB5GMjjj+X5133h61W0jWeFgxZucjp+H+etcJ4emQA3MIDYXJJbg12vhi9Uws7n53OCCeASP8KWhWp2dlNvtd6sQ56bRjqP8ACtqJLn7MgYg852Mf1rnbK6UlUdsR5yoHvj+dbVjraOwt0QsCCGYgc9/y/wAaWgI7HTmzCiljjrxV23mYhl2kqcAADBGawLWdkx5bA5PH16VpKWB86TJwOQpBwTQM14LoROoJ2KBj1yTU7XSWkbZlH3c8g8Y7Vj6eCsYdyN5HQntxz/n0q7eCOVd0KHB4YuOp7YoEWJ9QmdVPlgKVB3Y9qhjkuLhharwnY45IzUFpIrRvAz4wTtyOlSRidhhTjC8H/P0pDLyyPCApTcxbI4/zn/61VPFOjWfjLQrnQb7esVzEUyhxtI+6R2BBHvVqFnQiRkAKKfmz3/z/ACqO2lmFqYFX5d2fmJPzE+tDV9BK6dz5r8W/sa+L/jBo/ibwl411VEgubJYdJklm3IRLA6T/ACgExlS3BwQewx0/nX/aN+BHif4J/tMeNv2YLyG8uL7wf4mm0iPaOb4K+2KVFAziVSjqvUhx3r+r6W40fR7S41vWtQitrawt2lu7i6l8uKKNAWaRmJwoABJJ6AV8R+EvhN+x7+2N+0nd/t9+E/hHHY39pqlvHYeIdYs1EmtzWUeyK/SMu3lJt8kRuQshECMVXvzujShrY97LM9zfL1OGFqcqlbm0TvbbdM/Dn9pT9gn4w/sfa54c8NfHfSY9N1XXdGtNX/se3LO1tbyyMhilcrt81duWVCwUnBIORXkvjDU7ueYTrO7rE+Cpw2wcDHTkcfh6Cv6Df29Pgf8ADL9uv4S6h8L/ABvbm2vbRiPD+vwp/pGl3A6SA5G5WwAyZAde4IVh+Lv7VP8AwTp+PX7Ivhy88V+P9U0K/wBIhufIs7zT79g127nCgI6Ag4+Y9gAetc1ryuz9Zybi7La2RrBz5oVn8cr35mneLUUlprblXba/vHingC10nWfGtimqzRxWSTCa/mccRxINznsOgP44r6j+A37eHx28PnxMfAPjmXQtLn1JraSGGJcm33MEX58hQE8kcYOSea+RPD+o+IdVuJ9Ajigt7S42i7WGPLOiESbSx5xlVPGORXqXw30l5NL1LRICRPctEWQjkPdXUYXP/bOBGH+/WGIvHW9v8j6vhmnhc1xFONXDxqU1KU2pxVpTUWkknfSKu1fV3lppc/ZP/ggp+2X8QfiT4s8dfsufFDxbqGsT6fosHibQrnULhpZlQ3D2t2hZiTsLfZXC8AM8h/ir9FL1YxEDGQSXBbaOv+Ffht/wQy+JEc//AAVj0/TNFvAsF58ONR02Tac+cqZuRnHXPlq34Cv3Rli8qNvOTcxJGduB+ld2Ck5YdXPx/wAUMLhMPxliHhklCbukkktG46JabxK0VubydRExjBky2eox7/nT9XtDAioZmIXO1RyD2qncXcVo/wAi7c4OWPIHtVW+vpnAYFiOfnbuRXWfnqNRrmS4i+xRx5HXeeh/OsbWNP8ANj8sOo2rgLk4P40qao6yRwyblwu4vnkE9vSo729GHD5LFSVLDOf8/wBKBao5W+ilt5JbWSIY2EKT83H9PSsS9ixL9oyEUdAF4A//AF1013BFGjhjIqs/zNjgjAx+Vcx4okuIgEgJJDHPXbj6/Q/rTsK5z91dmIyWahdsbn5hwMHmsc3trExUxIv17+/FP1i5HkytIDjljgkn1rBTKKBHKQpGQFjzx+dNMQ3TpI7e2W28w5kYAYbrntXZeHg0LAxTRhidxLAnaM46Z+leaWty015HDJtDLJySPp/9eu48P6osEQjeN8gAAls4GCfxqSzv01GEGOBpQuRkEEYb/CtfSJLXaHhB34zjPTPY/wCe1cXY6naiMi4UhlI2lu59P/rVuaZrF20ipDGp5HBzg9sdaBnbQy3TxgQzKWDZCqMfqK07WG/llK3KlAfusGyCOP8A69YNhfS+SPkwzKcbSDzXRWF7EIllYEsq42n8KANPTZPKlCsmF3jBPAJx9PWrF5udmQkeWFBUZxz+NZ0epYynlAMz5Qg9Tj+lWLa5WO22zSklh2GaBdSdYnRRERjABU5q2uAfKaTJ4+X2rNGolpNu7PpnBwfXj3q28iwZmIJXYANvb6/pSGW5pIwCrcggHZv5HWiJ0KmbaQDgD0x+H0qhbOpUXClXZl4J7npg+1WbmaS8025ghRBM0DKoJ4DEHH4UCPCP+CgfiXwDdfsua/N8T/GN3pHgfT2jv/GMthATPqunwP5j6emGBRZ2WONjyWVmQAb9w/FCH/gsp8ZvCPxZ1TxV8JvCGmaV4SluEg0zwU8eIYLJVK8yLyJiQjFgCCWbjAAr9lfEEnwT/at+Cd34R8UQ2Xibwpr+nGG6to7xgk67v78bBlKunYhlK9Qa/PH9o3/g3p8DzWF74g/Zb+M1/Y3bOZLfw74wjWaFup8tLqIBkA6Dcjn1PeuGVScndn6NwjPhDDRqUc4hLmk0k9bRS9Nbt6N20W1tT4k8U/8ABSn9rvUfjncfHHwp8VbzSC0my28Ohln0+O2DblheNlCynnlyobk429K4b9sH9tf4zfti+J7XVviVqtvHb2MQSz0fSomjtIHwA8oVizFm9ydoJA6mtH9oX9iH9qL9mzUJrT4l/CTUFtULBdX0yM3VpIox83mJnYDkY3hT7V4izoj+ZKwIz9wd/akm29T77EZfwuo06uXRjp9pNv8APr99ulmdH8PNMhjdGaHNzfzrFbRnj5Nw3sfQcYz7H0re0jxo2k+EvFXxAgl2NqOpLaaOQcchSiN/wCLnP94L61y1jqc2naXNdKd+o36m3tEHWMMNuR6fKTj3xXo0f7En7YfxHttI8JeCP2ffEz2FrCTFLc2BtY5pHPzSbpigwcDBPG0CueUPaT1/q39Jfeeys6pZFglKDSlGMuXp781yxb84xlOT7e6vN+6f8EB/En9i/wDBSnwr4sdgiTSTaZC79AbiCSGNfxHFf0XTNeIZYmlCsRhWODkentX4zf8ABGf/AII/ftM+AvjRoHxl+O2m6f4S0vw/rceqfYJNUgury+lgVjDGqwO6xqHO5i7A4UjaSeP2UuLyGCHzz8z4OxSfwFduFv73r+iPyDjzE5diamDeHqKc1SftGtlKVSc0r97S17bGZIJbnEd2iMYxid145x2x0H+NVdRulA8pAGwcEg8Yp0t/JK6oinvvwcEZqC5W1JTEm2SQ/cJ645NdZ8CNVxMwY8kLkZGDjFUdQv7u4lOY2yp2gAjJ4HIqZpvKkkUr95eWJ5B9f5Vl3N5LbSkkYI4XPPGaBEdxdNO2xZyQrdCen5VzviSSdmkCyAlgeNx4A9Kt6i8AYyJMe/OcjPp7VzOs63dQSSlZAFOQBkZPfINAjDvdUsZfNiiGxlU4VvUdevXmuXvtVvprgyBmOf8AY/xArX1TUIbiRiVUl1OQq8/SuYvdage4JituAAPnwD/9egYzQZYIbqOacrkjCj+Vddpd7b4VN5GWwCW4NeX6XrUk8qSQyqGj+6BgA89+56mujsdTuTdi4V2AZuA6kKMfX/PFBR6dY3kJYRBfMbbncxJxzXQaZdTvIgW35AIyR/hXnulXMkMQne7h3kAEt6e3Nbml+JPJXalwxU4O4AHAPAznr0/WgD0fStRZ0wHAZThcHB610FjqZ2kyYyEAx715pomvafMztaTHLMDIqHkHHQ88f/Wrp9K16FdN5vGMaknLD+ZoA7fTrmGSAXJGW2nHI4JFTLcQXLi1gcg4yTj9PbmsKx1l2gUxttXbjlc4zVmz1oeXukw24hV+Ugnt+X6UAbkVu0SB3mAIPIJ6A5q6s08iLbswf0HUVgQa7azAWztGu0Z2LJnb16Vw37Sf7UfhT9mn4T6h8T9ZjMws1KWka5PmytnHA5OMEke2OpFTKSjG7HGLk7I6v43fHj4W/s1/D65+LHxf8TNpeiWLpFcXKWM05jZ2wo2RKzDJOMkY55Ir4/8A2rv+C437Mun/ALP+tJ+z34w1W78T6jY3Nnptx/Ystt9jdoX23IedVjcK+0YDFgWB2tjaeg8NfszeLvjjaH4l/tqeOtYurvUsXsXgWx1FrO20uLIdYJHhIeaQxgglHRY3ynzcNXhH7V/7AXw4+JP7Q3hb4N/s3eIr3Sbq30y68Ua1b6pqTXFhbW1vOq2au8oaQGaVwoZ3kGEf5G24rO9V62t+ZtGNFOzd/wAj55/aE/Zb/bG/4JI/CPwP+1n+zX8T7/UfC/i/QrKX4gW1zp5e0stVkUuokgkUFIHEgRJMK4dSrMpeMHY+Fn/Bw1odxpkOmfHf4H6jZ3QAWfUPCl0k8TerCC4ZGTr08xjx1r6a/ZD8e6T4L8b/APDGXxU8PQal8MPiSbzQ7jwdqkY+z6BrYhnmNtEnSG2u4oLv9wh2Q3NqTEEWZUX81v8Agq3/AMEwfiD/AME+fiW+veGbS51r4Ya5dN/wjmtMN72LHLfYblgPllUA7XwFlUbhgh1TnlC65o7H32S18pzpLB5jG1VL3ZrRyXnbdr53Wvc/Qrwl/wAFUf2APHyJD/wv6xtXmT95BrmnXNpszxhmljCD3wxHvimeJtH/AOCYnxanbxDqerfBrXmlfzPtEuo6bKzsCVyW3Z65HX1Ffhu93ZyjMMmxu6kc1nXMdsJfNSZVI98YqFFs9HFcIRox9phK2nqv+Af0AeBG/wCCenwW1eLx3Y+HPglocunRiVNUht9Kt3QZXYRKMHqq4OeT9axdU/bp/ZN1bxQyX37TXhK61DVZVSzh0zUhcquSflzCGWMdssQOme1fhb4L07RdT163j1e5hZWljVRcEeUgz8zbcYY4z1zz6V+q/wAIvgn/AMEsPj5+w83xQ1j4Xaj4L8VaXfr4dU+Htcu7ufWdVSLev2W2vHljczF4gYgoKYkIKqoepUU58t9T57Mskx+CwbxdRpwul8S5tevLe9uj3tdXSufpB+zv8WdG8J+KdM+FXiPRNUsp9Wtftmj6pcWimz1QMkrhYZFZjkLDKx3hfujn503e16lf2r3hLXKAFOEPU9K/L7/glL8K9T+AH7ROrfDb9ovVdft/EWk+GlvfBGk3mstPpdvb3AxLJChYhZx+9jxn5N1wgGcs36DXfizS47g3iSmSSJ9rjeeB9OnpXZQUVB2PkMRdz1OpurqO3ZZ47jgNgh1znGPTtWJq95cXUi35Ypsctt3gbex75PGfpXMap8SoHjka1mDMBwmRkcHH+fasWX4oQCGSS4uAHHQZ6f5/nW5gkegya39ptI5EfL5BPv8An7msrXNYiimGQGYffQEdeOK4L/hZYuEJhvAETJcxnoO2P8/lWbq3jwTxsBMWKHHOA2fTg0BZHW6zrMJhIEgV8nAVjn8a5HVtUiYsguC2cjJ6g/WuUuvEcyPJdSXjLu+ZhznHPUE4rD1bxjDIxhS7ZJ+QF5OSR146DjqcDtQFjf1zXLdDLsmJZV+ZFxnBBwa4LUNYt5Lkt9tzwPmHf1zz1zmm6r4mWWJ1N0GKnbKhj3EEDof05rkr7xHG8weJYiCgOc8HPPHHSgRNBqWqbvKuLo2clxHm3TaI3UnnODjPGeOvHIHStzT9Y1Tw3B9s1nWpJojKgMs3yiN3baFXkkgsygDsD9a8u0/xM2p6u2p6l4ls7iSIAW8ctkA4wfmZsQqQ23C5wRhe55rX1m/8L+J4bP8A4SnWryG4tbtZreW0uAI/MUcMFwdvUjJA6nBA6q5pynrNn8QG02JbPXNdSGRZlhRhMoUORnbhuS2O3XmtE+PrKwg+0DxU67VAaQAMpGCcBVAGcZI/HrXhl+dB1sQwXGo7YY3Cxz+XE4k4B2MMfPx8vIGPUdQ7SbOwg1pbdNSmsrSxtWGnK08e4K4XI4jbb90HLszDpuwTU8z6IOU9+svje4KHTvOliZm3XjhY0hA69W3buR1HIyc9BUmlfHbTTqMunJK1zdROwubaKLcYH6EMMAsR3yWryjTtctdOiuLay1qFXuJvMF3dgPE4XBztjRCw4K/e574qV/CWk6ldW2ra94fF8tsixQ7bNkjQDsIy8nLYwQ4IbjcCKLza2Cx73pX7SK2ISMmSQBeUhyQB2HygqDjJAznjp1xs+EP2ib3xXqf2C30+dYVfm4iZgnHHXHzenp1rwPR18CeGNSGrafoulaZewjMk1rbL5wywyJHCFTk8leAc4I5xV9/H9hBulR7sIXQQTrNsUqSBtBULI2eOctjr3yS8uwuU+lNR+Imm+HLgT37TbrlDtORlgoycZOeBk59Afavnf9u3x7o3iuT4fXTSy/2VofxB0671h2KuojF1AwJUnBAVXZg2PlU9qiHiHTr+xGl6lOIhGjAeTfvFMo6FWZD5ncgCRhjIOB1rK8YwfBLxB4RvPDviGQb57d41v765luFQtyRvbcCCR0BbP1OaipzSg0kaUmoTTZ6n8f8AWPid4p+CXiLTvgh4mW38Qz6dPDpVxdyxxiK8GQQrbSiNuBwRkZwWIB5+W/2Vf2af+CiHgez1T4kap+1zpvhvxT4nWNtUuNU8LR+IbxfI3LFC085Ij2biQqAqA4wSOlfw9+0xoHgqKXwR4v1ax8Tx2MD21nPH4rW2vFg2sqxSwyzRJMAHPzlgxwuRkHNr4j/8FBvCOrifw14Mex0Se6Plx6r4k16KWeMZLK0UMM8kfmK7yESSPhcjcr4AqFVju/u6lqnUjorW7nBeD9O+OS/8FDvA/hXxx+0R/wAJtev8SBdX1zaeGYLM35sbUT3E7mJjHEI2aSEBACzZznewH6Q/E3VPh/8AEXw3qfwr+L/hjS9d0LWAbXUdLvlWZJlOCMgLlGHykEcq3zAggGvkv4DeKv2dPhf4dE+jePPD2ra9NGXuNf1CIyG3EmDJHHKx3uWIDMRje3zYP8PprftPaZripYxaxp7pcNutLIyxs0jY4m2FisS/xAEE+nXNaUlLk95CnUaqqUHtaz226o/FL9qz9lNPAfxH8dweBtDvotO8LeJby1vbSSGVk06Hev2VWuCuGMgMqqWx/wAe55ORXifjTwRqHgPxfqPgnU9WspbzTLt7eeXT9Rju7V3U4JjmiJSVc9GUkHqCRX6W/wDBXn4MeJvjP42sviX8FtZ8HiWz0Z7bW4tPnitNRvXbdlpC7lJo/L+VQNrE7hhhtx+bOteE9Y0bWF03VLO4iupYFlEEnl52uMqwGQcEYIz2+tR7Poj7HLOKqkal8c3KNt1FX+bVn+Y7wzKsEsdnf7ZVaQbv3YwBn86/Rv8A4Ic+FbT4hfFbVfGF0ukX9n4QsyLKyuQstxZz3BVDNArnbDkJseTBJDBcY5HwHb/De2h0NL7WfGmk2DSqWS3lcyMT2EhRSqAjOB8xz1xX1P8AsKfGfwV+ydo2ra7ZpceLNV1u0WKLS0ihisLdlcMsrSxyyzS8bl2eSnDH5hnIy9mo1OZ7o9DOONHjsoqZbhqf7udryn8Vk01bXTVbt7N6H6PfHO43/tyfC/8A4RtzHqVpYanJqkbySyOls4QRh1ZRtU4uCMKByeK9f0/SPECRT3tmriGcjadhUIMfNiPbgcgcA+pr4R+Bn7Rmh6b451D4teOVub/xJq6/vyNFeG2solHywwK3IA6DIPAJO4sxPr9x+174Q1LTLqZj5cV/KRdQ3FtE3nuRwXDAY4GPlA6dsc7U+a7k1ufntRqyinse96R4x03Xy9vps80txauYbuGG4jbZtOCrAMcEev8Ahzl62LV7k2a3r2+UOyRtxDAcg4IUfXB7kcYrynXv2jLSw02xtba+0mGe4SN0WDTY/mRuFBCpk8c8tn0z1rAtv2sdTv8AxK+nxbUdJSzTzxRgSOoxkBFwpwOScng81qm+piet2upalozvNbJujlIESD5mbA+Y7cZUZzjDH8OlVdQ8QazNaPd3IuLR0HKzWvCkYOFfAyO/4/hXD6n+0trflrLo2rw30SnabW2ACRZ5OWIJf07c+nSs7UvH3iXxLcWt9LpTiCNFkhv4ZkiaA4JxuKhmHsQQfQ07gddf+INa1/SZp7O/RMbhFdMgXzNuQcDBLdCO3eudvtRsXgZb7xNbMJwquN6xzIAcBXGTgnIOGHfoOBXJaj8T9an1OfWNa+zfZY23SSWszyXDkEAO8ihSMY3HnoAPWub0uy+Gnhi3TxbBqXl2t/eyiJ3jCo02Tv8AMRy4YkNgtjcwPPFJOXYLHo9wzT6idKW8EjPCXhjF065UgYG5eD8wON3I5A45rHmSEOY7pkd043SSkkjtyTyMd+9Um8Y6jYSDWNM1axvFXcyJc7BGMgn92UAyMH+LP881NZ1zTry88+++FOlam7IP9Kk0lHJHpnPOOarcR5pBr/iDyvsMuoiWObeBLauqgtjBR2ZVxgDHygnkjPJNT6JqNhFCuq6pcAW6PH5n2xf3W5R2DfNI3JycYFee2mvXJ1BYzojeaqeXFaRzBEjwOc4UEEEkkdeDnHONvTfF6yuLXUdUuvMG9HurdfNjtwCBuVQBnPT7oUdRk00kVqejafrMuoWHnQQQ2tssmN0EjCTaxO1QTny1OcAYGecBsHFiPWtNsIhLNf8A2S2Eu3y5flkeQdSqse2fv845Gc/LXl9/q1xpUkvh+2mvLhbdTJu0Q/61zHwSxA3qvIyBxhufmqxqGqvZtbeHNRE+oJFbF473Tr3c4iLFyjqVIOCTnBBGeScYqtBas9OPiaeGE3aanNEsv+ojW5CSOnJDtISCFz/dznHbrVq28bavo2nLBPqTReazTCBroiIRsAQ7EAs7MScZbgeucDyG88XS695On2t3A08dsvkXKSCQpCOglRSpO0YBIztHtyF1nxTr3i23lbVZNON3p9okUl3YSGSGdVO1Q4ZcKecZ3HkDCnINLQLHs7eLIba5TSrq9he92sRE10EhtjjovTLDnIPyjgc4zV3/AITXSW1CdLfxHbXbJbqLi+GX4HBEYHQHKjtkAZxkivE11jX9bu/Kl0aazuLUYfVo5gsEwwoDksQQeDygyc/cPWtjRBqd3DPfajBe6bcQoVluI4wTcFlyI1XcDk7T/CV6EgUgPUYPFQl0y6gtU+z2VrOgMEK7zKz5wzlUxtGOGIABPHOTVy68a3ENgmrC6lhEgKwQRKyqqqAvPKgHnI6k8E96828Ox6rBas89vPazI+Y3t4mkZz1YOuSGXHX+HnHpRf3MmnrPe6dr9xLdXIBfTrO1doQBnmSNhIQB2TjGSRtotcNj1211fXNYtbXT9PtLm/e8iSR54bZppGQqM8IDkAHB6ZPHYCpx8Pbm5vxod78JdXhtVlbcw0KUxTueQSViORnHJYBefpXp/wCx7a6bB8DLHXNP0/yZ9UuLie7WBWYHbM0a5D5K4VOmRjn1Ndta/wDCwEkWK0u7REkG7zPNZtg80ncY9vJ8vggtwT170+UnmPmr/hTWo6xeMur/AAx1QC1LG2hbQZli+XOE+7jBOTjO1jwc55yNX+CUt/ZXkekfCbXIrq6k/wBJmGkXcbmPK8LuBGc9RjJA44zX1tbjxTFqxS/u45raSRhFAo+RIwDtYZG4uSFyS2PmOACoLV7O48cSadLYXmm2FvMLFjFeC5klXzQCARGY1wM8435wMc9aOUOY+GPF37Gdz4l062Ww+GOqxvGpFxJJosxdssWAJCkkbSBnt7dK4S5/4J56tpnieXVNL+FGqvE85ULBokyIAVwM/LkD3P4c1+kUUvjrUNHu0tLeygmaExwz/bHlIkYYDbWiGAOuOfoaZeWXjzTbaTz/ABQt3czqqwRTWgUW/OGkyhBfjOF4GVAyKLC5j87PDP7Afi7S1mj1L4eaqqSlPJlXSpnRMHJyY0bbnI6/jjt28f7K3iOy0yBrT4e6ukloNqf8SWbY3f8AhQ/NknHbgDivtPUrbx//AGRZ2OneIo7a9+0lp7xbYSkw7T8pXKgNuIywwMLnAzgQa1F8U7awtLDQvEcE+oLI7XF88Ih3qegCqrjI5ycgH86dgufMWkfB7xZp13Fqk3wl1tjIrtPZPp8rwMGJBAZYyVOMHHXn25SL4W+MtGnntofhhrTQTIPNsjpk4OwcjbL5Y+cYzg4HbknFfTTWnxHaO006TxYkN1H5pvLm1slm87JHl4GF4Ck5P885qDV7L4rwGwjg8U2QlRGjvwi5V33cOoVGZcD+Fj17Glyj5rnypc/C/wCIlxJJZ3fw614QREtYyHQblZR83oxUNx79eRxnOZB8Lfizf3qzD4c6uGhXi6TSJE3HtlJEB6Zyec54yeK+xLx/iVYGzilksbtzDALiLzzERKrEyNhYicOpAGQpUjOOeI7mXxlDaSxy3cDXDt+5RptqR5mJPWJjxGQoJQ5K52jNHKg5j5GT4d/FbTmYL8PvEXkyyKPJis38hiSchgY/MQDt8vGTyKSTwF8Rll+y3PgvxPJAE3RBNImOzODwVTdj2OOpJFfWM1l8TU0q6DahbpdO0RsXluVlCKCd+5lgTAIK4HlnBzzyALHh228aW+ny/wDCU6nFdTSThonWXaBFt/65KSdw9gfXiiwXPkGDwZ8U4POmHgXXR5qsCItCuATkdWyvueh5yc9BWJrHhr4n2C/Y0+EviG7sJAGNu+jXjbHAwG74bBPIHRuvavs7w5p/xCiuFuPEGpC5AhYMYrtDEzBcZC+QrAZP3TJkYxlqzY4fiRZlludVhSb7NID5zLIofYQhCLBGRhiCSWbgEYJIYFkK7Pii68L/ABrSxgtIfg94lmtVJBtf7Gu18g56htozwTyQAPerVz4I+KE8xMnwb8VyFQF3w6O+04HUbeOevBPXrnNfZ2mHx9Jq9pHqmsWc1nBvWWGO3ZZJxglWyzEIwO35Rxwx7hV2bqdZpMs0se0bQjkkgfgf6CjlGpn/2Q==",
                    "file_type": "jpg"
                }
            },
            "addresses": [{
                "address_type": "headquater_address",
                "street_address": "F102",
                "apartment": "ABC Apartment",
                "city": "TestCity",
                "pincode": 123456,
                "country": "TestCountry"
            },
                {
                    "address_type": "mailing_address",
                    "street_address": "F102",
                    "apartment": "ABC Apartment",
                    "city": "TestCity",
                    "pincode": 123456,
                    "country": "TestCountry"
                }
            ],
            "groups": [
                {
                    "name": "my-group",
                    "id": "",
                    "payment_address": "0x123",
                    "payment_config": {
                        "payment_expiration_threshold": 40320,
                        "payment_channel_storage_type": "etcd",
                        "payment_channel_storage_client": {
                            "connection_timeout": "5s",
                            "request_timeout": "3s",
                            "endpoints": [
                                "http://127.0.0.1:2379"
                            ]
                        }
                    }
                },
                {
                    "name": "group-123",
                    "id": "",
                    "payment_address": "0x123",
                    "payment_config": {
                        "payment_expiration_threshold": 40320,
                        "payment_channel_storage_type": "etcd",
                        "payment_channel_storage_client": {
                            "connection_timeout": "5s",
                            "request_timeout": "3s",
                            "endpoints": [
                                "http://127.0.0.1:2379"
                            ]
                        }
                    }
                }
            ]
        }
        response_org = OrganizationService().add_organization_draft(payload, username)
        orgs = self.org_repo.get_latest_org_from_org_uuid(test_org_uuid)
        if len(orgs) != 1:
            assert False
        else:
            groups = orgs[0].Organization.groups
            if len(groups) == 0:
                assert False
            self.assertEqual(orgs[0].Organization.org_uuid, test_org_uuid)
            self.assertEqual(orgs[0].OrganizationReviewWorkflow.status, OrganizationStatus.APPROVED.value)

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock(return_value="Q3E12")))
    def test_add_new_org_draft_one(self, mock_boto, mock_ipfs):
        """
        Add organization draft with type individual, org_id wont be given
        """
        payload = {
            "org_id": "",
            "org_uuid": "",
            "org_name": "dummy_org",
            "org_type": "individual",
            "metadata_ipfs_hash": "",
            "description": "that is the dummy org for testcases",
            "short_description": "that is the short description",
            "url": "https://dummy.dummy",
            "contacts": [],
            "assets": {
                "hero_image": {
                    "raw": "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",
                    "file_type": "jpg"
                }
            },
            "addresses": [{
                "address_type": "headquater_address",
                "street_address": "F102",
                "apartment": "ABC Apartment",
                "city": "TestCity",
                "pincode": 123456,
                "country": "TestCountry"
            },
                {
                    "address_type": "mailing_address",
                    "street_address": "F102",
                    "apartment": "ABC Apartment",
                    "city": "TestCity",
                    "pincode": 123456,
                    "country": "TestCountry"
                }
            ],
            "groups": [
                {
                    "name": "my-group",
                    "id": "",
                    "payment_address": "0x123",
                    "payment_config": {
                        "payment_expiration_threshold": 40320,
                        "payment_channel_storage_type": "etcd",
                        "payment_channel_storage_client": {
                            "connection_timeout": "5s",
                            "request_timeout": "3s",
                            "endpoints": [
                                "http://127.0.0.1:2379"
                            ]
                        }
                    }
                },
                {
                    "name": "group-123",
                    "id": "",
                    "payment_address": "0x123",
                    "payment_config": {
                        "payment_expiration_threshold": 40320,
                        "payment_channel_storage_type": "etcd",
                        "payment_channel_storage_client": {
                            "connection_timeout": "5s",
                            "request_timeout": "3s",
                            "endpoints": [
                                "http://127.0.0.1:2379"
                            ]
                        }
                    }
                }
            ]
        }
        username = "pratik@dummy.com"
        response_org = OrganizationService().add_organization_draft(payload, username)
        test_org_id = response_org["org_uuid"]
        orgs = self.org_repo.get_organization_draft(test_org_id)
        groups = self.org_repo.session.query(Group).filter(Group.org_uuid == test_org_id).all()
        if len(orgs) != 1 or len(groups) != 2:
            assert False
        else:
            self.assertEqual(orgs[0].org_uuid, test_org_id)

        payload = {
            "org_id": "test_org_id",
            "org_name": "dummy_org",
            "org_type": "individual",
            "org_uuid": test_org_id,
            "description": "this is the dummy org for testcases",
            "short_description": "that is the short description",
            "url": "https://dummy.dummy",
            "contacts": [],
            "assets": {
                "hero_image": {
                    "url": "https://dummy.com"
                }
            },
            "duns_no": 123456789,
            "mail_address_same_hq_address": False,
            "addresses": [],
            "groups": [
                {
                    "name": "group-xyz",
                    "id": "",
                    "payment_address": "0x4356",
                    "payment_config": {
                        "payment_expiration_threshold": 40320,
                        "payment_channel_storage_type": "etcd",
                        "payment_channel_storage_client": {
                            "connection_timeout": "5s",
                            "request_timeout": "3s",
                            "endpoints": [
                                "http://127.0.0.1:2379"
                            ]
                        }
                    }
                },
                {
                    "name": "group-pqr",
                    "id": "",
                    "payment_address": "0x123",
                    "payment_config": {
                        "payment_expiration_threshold": 40320,
                        "payment_channel_storage_type": "etcd",
                        "payment_channel_storage_client": {
                            "connection_timeout": "5s",
                            "request_timeout": "3s",
                            "endpoints": [
                                "http://127.0.0.1:2379"
                            ]
                        }
                    }
                }
            ]
        }
        username = "dummy@dummy.com"
        OrganizationService().add_organization_draft(payload, username)
        orgs = self.org_repo.get_organization_draft(test_org_id)
        if len(orgs) == 0:
            assert False
        else:
            self.assertEqual(orgs[0].org_uuid, test_org_id)
            self.assertEqual(orgs[0].short_description, "that is the short description")

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    def test_add_new_org_draft_two(self, ipfs_mock):
        """
        Add organization draft without org id with type "organization"
        """
        payload = {
            "org_id": "",
            "org_uuid": "",
            "org_name": "dummy_org",
            "org_type": "organization",
            "metadata_ipfs_hash": "",
            "description": "",
            "short_description": "",
            "url": "",
            "contacts": [],
            "assets": {
                "hero_image": {
                    "raw": "/9j/4AAQSkZJRgABAQAAAQABAAD//gA7Q1JFQVRPUjogZ2QtanBlZyB2MS4wICh1c2luZyBJSkcgSlBFRyB2NjIpLCBxdWFsaXR5ID0gOTUK/9sAQwACAQEBAQECAQEBAgICAgIEAwICAgIFBAQDBAYFBgYGBQYGBgcJCAYHCQcGBggLCAkKCgoKCgYICwwLCgwJCgoK/9sAQwECAgICAgIFAwMFCgcGBwoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoK/8AAEQgAsADcAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQYHCAkKC//EALUQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+v/EAB8BAAMBAQEBAQEBAQEAAAAAAAABAgMEBQYHCAkKC//EALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXETIjKBCBRCkaGxwQkjM1LwFWJy0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/aAAwDAQACEQMRAD8A8+8OWAmuHknJPyjBxnnJrfOnSzfuI4mLD+Ijn8fzpvh/TJY08548DJIIGTgfzrds7VJHaRoiDgdflBHGO3sKyNCvpWhQpvIKBnbLMBjJ9a3NKsjZ3jxyL82w4IJAX681Clk5iSW0VgEIMhAHGSR+PU1uWOm3U+pJPNG6q0BBOeMdvpx+efahdAJ9KsIZ0M1xG7jPzkEevv7c/jVuCxSS9DW7hkMnKkYO085/pmtbQNBkgUlE5CqSmcEDJ56dOK3G0GBbiOaKJXxyVK556dqYjPFrJDbedg4JwoY8t2FZht9RbUhDOuV3DzMjAz/9b1PtXXPoiyRxbY33rLmP5c5Yj/69WbTw6DdtGylmVchPQY/+uKBJGDpWlpZqWtoshF2/Mfvc8/rU9ppV0YZpHA3Bz+6IyVx2/Kukm0d2CwwQh5Oi+g4yc/57Vrad4YFio+1KMyOdvy8fjQFjy3WdEuYNUW68oKG+UoVyCcZ4H5/lVnwv4Ym1EpDLbYBAbanHQgjPcniu/wDFXhdbqAvHFGFLbVxyCe5/Co/DegX9hZTsqBrkKdgVchjkgYx0oGtTkr7SIbfUZo4mRSB6fdrK1qwjDx2tqFeRdp4XkZ712d7oNzHK97dqzSZ3MP7xz9KS38OtMUnvY1SVW2gIpIIPOPwxUPcDml0YSne/l9CCSv8AT+dRQaXMIg6RkIn3S4xkZNddrfh/7QgSwyTIAUGPu46n+VSt4ZQJGrBt20DGR1/z/KrA4u48IJcSb5pAeOI1IB9uPzqte+GmhsGhNqThifmOTXolp4ThltFuFLBYg33s5Bzjj9ahuPDZuYftY3IME8jPTj+lAjyR/DrPObqSOSV2wMEY2jtWL4h8PPdzGBwzHHGeQMkZ/DFev3XhefBV1IVxkbhxjjJH5/rWdrfgtd0dwtsPlJ5C8hSvSgdz59+KHhSKCKHdZiZUcKmWwBk5zxV+x8JRnT7VPs7CLKnAPCkDk/zrsfH/AISFzEkVujArMpG5eR83t9a0tc0f+xNAt4YtODvvRZyuTu4we3HH41K3GcNfeE5YIiuDtJByw6LnP/16SDw9b24AAGABjBB7+3fg13t1oyXsrRx2+VjUDDHnBqu/h8sJIZoFAZSQ6+xzmqJORurSWSLKFT68e1clcaBic3BcB4zkEL1znj+deoXGmxtHIhVhEFAUrjk+o/SuX8U6LLask9tvyQFlVRkLj19OtAjg9e0jzrdcvtkVNvDYCknn61nJYPFlJQ7HPB46fjXcazocMulp5iCNh8xZDyCeazLfQ7R4VaTzs47img1O40Xw3cW6Rfabc42kfL2/A/lWodGebY5tid7nauOOP8k/hWzpejlws8srABiOD1x2/Wt3SNCiEhEySfd4BXikWc/p3he5gjS2MSDzZOTIuAAP5/1rpbbw1ZxY8wA+WBwO4PH4c10uneHIbow3DxO5L/dwSoGMf41raf4SaS+RzY7IyQF7bgOpJ7UAUtH0xPLSGOPaQuHAHUVvWHhO2TYwsyQeinB5z/8ArretfDP2jcyx4U/cz1z9BXQWPhKaMLIItseOWwCcnil1EcdP4SVQqraZaNgzxqu3IHuPY8VsWfgizjnj1KSJWPkeWqoOo9T+Rrt9D0QwW3n3BDEZChgMEdAcmtCy8OaZcu0n2fY5bAKjjrzTA4a18BwLI7W1uQDyRjv9Bz0raHhJLm1EcSHEZ7pg+/Wu7ttBsrAeXbwAEgYJ65PHWmvok8wZmUbQeVXjAFAHmWveFkOpLbWtokZClVeVSVPfpg9D/wDrpdD8GuLd3hUyPFK25WGORivRpvDVizl2uW8w8tk5IHoP51Pp3htFjmABELOXwV65+vXpQB5Fqfhva8qSx/vUYIuAOmMn8zVG08PlrtbNhkHhiDg546H8DXq3iPwpEJo32Mf3oyuRzn1P+etUW8KLbSiVLPbKGG35uOO2aVtRnEyeCbSOOKCFHEatnzFPO7nOabJ8OJLiVXiZgg5w4+/3zXoNppDTK9tb2RTCbmz0z1rVXSY0CRPbKMpgDkgc9qYjzex8Bx22biDZIArKR2Jz9evB59qqN4MmZCZIDhzgqqjAGa9asvDlsIxG0JYZ4Lp2OTwP89KqzeHogGl8lwpH8Q4PPFAmzyK78DzmZZZoo9nRZGU5x3GO3TFRX3gR5HMUioyScJ9OOceteqav4d+0stwiIAvDZ/hx1Pvn+lYes2SRy+ZHgEMNzqnC8UAj5+8c+BJEnRGQhfM5Vhyeen547+tO17wyLjSRBJbnJIaIKo+9kj+n+elep6r4Ze/njvU2sVlVkjkbA+9gn2x1/CqvizRFtLJI/s4RXlUA4HrxyeeRSsM8u/4Ri4lRy0YVgo2MepIHt+NQaj4ZktYFhaLLsDtYDBQEdvavUbPwvOsPmbCGI5z1UcHpjrVTVfCe6VnznjEjEcAUxWPJbrwqqQJGIsKeCATnH+f5VzPi3SZbG0E9kg+V1XBGdw6f5+te0ar4ct4fkEB/vKdvA4/lXG+JNNs4blNOubTZHKNqlsgH/A9KYrnkOr+HVu7cS+S0TrgOgOef8KpRaa9unlS2BkI/iIHp7n1zXomqeF49MDtl2V2wu/nnIwOcVnR6M8IMQtHcBjg+lC0A6bSbB5EC+ahkZTtyuOv0/Cul0nQZbVwzOSXXAJ46/jxVrSPDsSNFDMcBgNuBxXY6L4ejEbQ7A+OhLYPXGPpSLG+GtLQ26W4VnDnkjnHTv/nrXS6dojTuymIYRj9PpT/D+gJaDzBCkSqcfXjrn0roNBsLme6ZnBdSDwDwcccH/P4UAS6T4fTerzRMPl7Hr+dbdpo8jNhYip2nIB6Ve0yFI3DeXgRgde4rbsVt5pMRwvkqcqR1oEY1hpUj5gWAMi5B2ZHf/IrXttGDW/lCInJyrY5FWxYzRoLq2fCp95UTBP4VbjDJZANuLHg5U4I9iOnWgEVodIMZiiXseT+tXJrOOIhHizuPL7OoPartrZ+Yq7lPOMMVyDnv/OrNxH5a7I13sARkqAMdsd6AOZXw9DLLK9w+0SvtUOcEj29qu2WhTNbGDhtiEEKMgrnpnGM96vPpH2x2DFAAcgPn0x7YrV0ezjs4Hj3ZEfykjpjHHPegGcFrNi0t6ltbQb9vKZ6Hr0J/GoxpdzOu2aEK69vLx8vTg102p6bGb9bq3G1wASD09zinT2SyTJdLOgUj5weu314pdQMfTvDECyK6QkB1O75RwTxzVm+0Y25RUkC7RkEpjAxW1p2nrb3DOiMdyEhTkjr19qdNpi3EuHJbHzbQOBTEc5PbiGbzQHbbhSBzzjvn/P51YktotRCjYysG4XHTHTmup0TStGhvGn1aOR7eKNmeKIfNJheFGPf+dYfhODV9RsJb/wASabDaXEtwzQ28R5ji6qG9SM4PTOBxU8y5uUrlbjzHM3mj3Edw2/nJ+RNp659fzrC1Lw6y5N0rFnk4Cj7g/rXpOraYm0mJtxBz0/pWKbCKacrnBDkZ7Eg9BVErY80vdKjiuBAyE7ORnrjjgfnVTxj4fldFhliLRo4YY/h7/wAhXZaxoSS6qVkDYjcbTjBGKr61bTvbSRyRAKEG3J569DQM5CKweWMNCSRswfm6Y6ZrN1jTMxeTLIqk5zuGcj0/WuytNNhFhkty33iOzYqpJpqXDGOXKKVyMr/9agRwGreH38hZ2IIjGF2ZAx/n+lcH438PW17/AKRcqEdBjaO6568fnXsms6FEXacSj72AxPQY/TtXGeKPCzrcs8UhMbKDlsYDZ6d+1AI8f1qN3i+0ysG2HbypwSOhrJe0lOFa2IYDDAZ4PWvQ9d0axtiYpF4U5KHHU8Zx6D+prnruW3jnKxnI75B6/lTQj0PT9OgkMb/Zt7jkAkH866bQLUJKC6RqI/8AWgEk5z2rO8O2stq6si5xgb2HPIzjp9a6WG3QR+YAVHdtuPxGPwFIsuyvbRSRxR2xVpSd5Ze4Fbuny20fliC43RRjlfK5Vh1HH1rBvY1WVIDuG9ARgZ4zjoP8/wAq6HwVobyQB5QSC5Iwv8qANvSmluQxQEpv+YkEHOP6/wBK2NO82G4KNcfLgbdvYdxnt1qfT7COSQCNFACkMMd6tT6DDLCQkHU9e2f69KBal6JEkYJGzMuPugf16VYuHiuViRbZyQ2N+3GGPrTdLjbTrdbNURjgbFPH4Z/L86u2doLa9DSybTJghfUnj8aAH6cnlq0ciAYB2gHrzTi3l7wFLgjkBf1q99ikhVl8qUsT1IBGB25+tKdNDn7OLfgHnA6j0+tAWMy2isrqQyvbkyFSAueMdfx6Vnaz4r0Pwjol34j8Wa5Z6VpdnGz3d/qF2sMFugPLu7kKg9yR1rW1C3NvcMEjI4yyhen0qj+0b+y5+yP8ffA9n4F+PHgw6zDEhkST+0bmMwyEZ80CGRRuzwDjIBwDUykoq514KnhKmKjHFOSp395xSlK3km4q/q9N9dj5D+MP/Bcr9gv4aa02k+H/ABLrPjKVD5csvhjS1a3Rh1xNcPEHH+1HuHvXLWH/AAcA/se6uQl/8NvH1qQCBJDZWM4X6gXQI/KuX/bk/wCCFzpog8S/sKz3Mt4ny/8ACH+IoTdWt0irwY5rhmlic4HcoSRwuS1fA/hL/gm5+238Ydfk8PWH7LTaDcwnbNf3GpfZoN2WGQCX3jKEfICOK8+WJrKWp/SfDnD/AIAZjk6nWrVI1Eve9rNwlf8A7cThbtp+J+mOrf8ABfr9hTw3p73MGm+PrxggxbRaBAHJGeMvcqv61j/AP/gqp+0t/wAFDviq3w+/Y0+AsfhLwpprK3iz4jeLJRdvp9u2flht0CxfamAIjRnlBPzMoVWNfPXwO/4Npfjt4s1a2139pD47aHo+grIDcWHhgT3d9Ko+8gaeKKOInoHxJj+6a/Vj4D/s1/B39mD4V6b8Hfgx4Tg0XQ9NjIihQkyTyEDfPM5GZJWIyWY54HQAAdNKVWqrt6H53xfV8NMmcqGRUJVqnSc5uUY+aVoqXkmmur2s9oeJIllid43MjKAzSKASPXgev05NJbXQup5MQuv7zG7O4857jkf/AF604NEsZbsXKQROduM5zn86nbSxE2Y7aMKcbsKAc44NdJ+SPcxdV+S1EqSFWYHejJ7evasfTZVmlZ1gYmNSAFAPOODXTX2iSzIWgU7mX5l5AHv/APWrE0zSG0xJZ1jj8xlzjdkZz1+lAJmNfRSSyrI1oGkJIJZsAkfTpzVPxDpVxcWrqsQ3FQZAT2+pNdBHExxKFJYDj9R+FZniK7nubOWKF17Jt2fdBPU4PsaBnJ22nTupjnYhRz8oxUFxpds6DiRncZ5Y/KMdq6S2s41YRhD3OCMD1/OopbD7O4eQchvvEZ+n86AucTfQXsZKyHO7IG7v9Of85rjdd05ry4Bv51jkjcmIZIJOcdK9U1myhmwCoLKeGxjqPSuU1XwtCG803GXQ7idxP4frQJM8v1Dw2r5BuGHUuMAHHZenTOayf7BsLdjF5aHB6lc5/Pp9K7fxXAijKxSHBITauC2OvP8AnOK4u8vLg3DeVGyDjKNNgg478HmgDt/CQS+DMyggOOHHy4A9vwrr49qW4ZlXb/EQvToMAfnXKeFLFAR5M4QFv4RxXX6QMKbeSTLOfmxgDHH+fxptjsOltvtDwBQ6gnYD0Ars/DEPl+WuwBScqAckjHrXP29kL51tLeMK45DenSur8NWskKeRknjGSMnP+eaQzasrmOK+2I4C4ywfvWvb3Nw0oCkCLb90jPNUk04TPHM7Bdq9QcE1p20ZhlWKAgjcQ7EZ/KgAnhlISRoFBBByR0OferFpYXUt0ksvVMsue30q6Le22g+YC2MYIJ5p7SEFTszgYJAP+RQLqWLEyTMzSDdu+6c5JonneBwY1fJyCCMHrSwxOIVwRzyFz/8AXqwLWecEDdmIfeAAFIZl3lvBekyPGdw4HBz+dfIPxd+In7Yut/E3U/BXw3+IM2maGmpv50kPkCe2VgNqxnyWd1BZRww2kE5wVB+1IYhPILSFlRuS5UDGMYNeAeLPAPiq3+JtvdeEr9beSzuJJtXg2GVJYNwACRsdqSFWUGYqxwDj1HFjYzlGNnY9HLatKlUk5xvp1V/zO8sPH+neEvCdtfanrc9ze22iCRY7qZkmupCoAVzJ8wJJU44Oc+4rnrr9o3wj4R+BOv8Axl16/j0q08P2bW+pR3gSe5hywRo1XudzqiZ+8WHXvxv7YMHxF0vw9b/EaK/sLC3j0ye8vtREePOWLLNAjr8iuYlYBW+9g4Py4P5M/wDBSr9trXviR46sfgj4C8RzweHYLGDU/EdtbzOEuryfMqq5blwkUikBvuscYzGDXI+ZH2nBHC0+L+IaOAT5YN3m+0E/et5vZX0u1fQ+q/Ef/BeX4qwa/PB8PPgz4eTQVCiwj1R53uXA/jeRJFXJ5O0Lxnv39R/Zq/4Lm/AT4i+J7bwH+0hoLfD67vpPLs9fku/tGlXEh/gkk2hrZs/38rjJLADNfjZ4y+KsnhXwrNJZANcyXbQxszHCZLEHA/2a47RviNqfiO8/s6/nt5BOAkcc0alGYdAd2cgn1zzz1ArGhXxUfevof05xp4a+F9HDxy+jh/Z12laUZS5lfa92027dU9z+qqxVZoY7/TbtLi3njV4Z43DI6MMgqwOCpGDkdc1bRbuSJUdwqcMowc8H1r8KP+CXv/BZz4l/sP8AiDTvgZ+0N9u174WX10YbBpnL3nh4lsMkLMfmRM/NCxwfvKVJYH91PCHi/wAH/FDwjp3xC+H/AIjttZ0LV7YXGm6jZy7o5o27g9QeoIOCCCCAQRXs0a0asbo/kLiThfH8OYp06qvC9lK1td7SXSVtbbNaxbWo95biK2bZIgV8gnPzdetczcXEVvPLbSqfvEh+gIz6V08qRI27ZkKxAA9ayLy0jvHkiMY3sOW6celbHzVjAilMuf35yzfJj2J/Osu8s7s2ZtmuHAJywK4zz1JrabSzazSIxLZB2jklTn8qh1CJ/LWKVC0hAOVH4HofSgDF0nT5ot7zOeDtGFJI9M/hmrBt2ktywdS3TGOMdK07M2NtC0U7MA/A59qyYg0epeXAvyPyzZ4AoC1zI1SBopmTbnHYjOMYz271zHiUXMEjyWKFcqAeOnXqOeen5V2+tS2wmR4i7Hed7J0HHf06Cuf8RwxvaCHzBDwdr9cZxTFseY+ILqO6jCw2+6aNGjLZIUcZ/wA8dq5200e7mi3SQucNgFiBkDvxXbajpcJ3Ryxn5s5bJ2E9Aev0rJGnGL5HkZTnkYpAWfDdkWiDMUbaflBY89813Gi2lv5irFFuBGWYNg5/KuO8GGaSVZfMIC8A7jx/nNdrohW4uv3aYUNwSvOB1/Wgo3bKwHmJ9nh2kYySeTk/57V1GiWTJbecwVSGJ3bv6Vj2ECG5BU4PBbnsPx/ziujsIlitEhES4bg89KAL+n2qyxDIzvHGSKv21pCZiqMh24yuc4470WcP+hiRYhy2MGtNLeCCPzIIyM5+93/GgCK1s2JV0XcikbQv+f8AOK0bGxtYxI+3cSfXJ/z/AIUmkxxyKsgHPRgB7Y/GrsAcwBwdzMxJcL0HQUAVEt4jKq7HPQDYeBVuLytkuzG5QQd/Ofp61EJpftBYLtGOCV6n3oM222aaJQxySSCO3c0gHWdkrsStsy56MvGP1ryD47aXrd38QRqGkeOrPQFtrKNJGljGZ8NvYEnqMDGO+OAeK9ghvJFCR73GG+Ycc/5zXk/7VvhXVb/SV8U29lFLa2UURIbO6SXzCFG0Kc9RncMdB61jXTdLQ2w7Sqanyj/wWJ+OPgD4XfsZapL4l8U3E2rQxW8WjaTFOBbX91uywlX+JCu75Q38JwDivw/8ODVPE11ca5dzNPeahc/vJX6u/wAzSOx9MkH3r9bP+Cu/wq174zfB668M6kz2+lWuiNqWns8e1kv7eOSQB8LhtyhlJGB97HJFfjh4fbXL6wZ31pNNsLdd0sjyEZ74AAyx6flXmy95M/ovwSx1HLsVWnyuTaT0tpa+rk7JKzd29jY8e2xtYZF1RXVPOAjaNQ3QHG4fQ9q5CXTdMvJT/Zd8ob+EA7f0q3qfxTudL1aSDRYft1p5Ucey9RsNhfmb1GTnriret2WmxWMOpato62Mtwx2pHIWC4GeRgFOvTk8dKcYygkmfrmbZ1kXEdarKjJN0/iupWWrV1UV4tPpoafh/xIniOyPw1+IrDybpkSy1Z0/eWsy/6pmP8QH3eedrMM4xj7i/4I5/8FVPEX7F3xcsP2dfjxr1zZ+BtY1IWep/2ru8jTJydi3sbHO0AhRIR8rJkkblBr4I0PVLL7dDY6pNBdWEzBJMygvGp7qThuOvPp+Nfop+wt/wSf8AC37Wnh3U/FnxJ+KVza2kDxTPZWNmrTyx+WrFvMkyiBiTk7CeaUVKFVci8/6/VH59xHXyX+xatTNKy5H+7u4ucpXUpQWnWLTdOpfTVS0sj9w7+zkm/wBLsp4pI3VXRkbhwe4IyCKpT2cCRuVY5YjvgrmovhRHpNj8K/D2j+HG87T9O0WCytnL7iVgQQjJ7/cPNPmlBcxxhkJcAPjqc9MV7Cd1c/lSfKptLYotEvml2LkKCGyvfis69gkNwrxodv8ADkniuguoEa8baXZipDAnofTioL+2PkhjENrAYAHA/wA80yTnUsrqSPY0AGG+cvyMd6rahpjQNut0XaGAJJ5I/wD1V1xs4Psa3JBUrgE9/wDGsi9t1eLzGl3xk/cbA+v9aBnLXmn2MsjIs2zn5cMOlYuv2LywzGzkA2DADL1xz9AK3vELWHn/ALuFt23Ckc47nGawrl2kzaRMdjgMp7jvQS7nF6to9xNp6s1zudiTtL8A5/TpWTd6K0ly7DJ6ciQEdB6muv1EAW2y1jwEyCY2AG7rxXNXnmC7kEcb4DdVY81SQrsoeG45mVYfOVSXB5GMjjj+X5133h61W0jWeFgxZucjp+H+etcJ4emQA3MIDYXJJbg12vhi9Uws7n53OCCeASP8KWhWp2dlNvtd6sQ56bRjqP8ACtqJLn7MgYg852Mf1rnbK6UlUdsR5yoHvj+dbVjraOwt0QsCCGYgc9/y/wAaWgI7HTmzCiljjrxV23mYhl2kqcAADBGawLWdkx5bA5PH16VpKWB86TJwOQpBwTQM14LoROoJ2KBj1yTU7XSWkbZlH3c8g8Y7Vj6eCsYdyN5HQntxz/n0q7eCOVd0KHB4YuOp7YoEWJ9QmdVPlgKVB3Y9qhjkuLhharwnY45IzUFpIrRvAz4wTtyOlSRidhhTjC8H/P0pDLyyPCApTcxbI4/zn/61VPFOjWfjLQrnQb7esVzEUyhxtI+6R2BBHvVqFnQiRkAKKfmz3/z/ACqO2lmFqYFX5d2fmJPzE+tDV9BK6dz5r8W/sa+L/jBo/ibwl411VEgubJYdJklm3IRLA6T/ACgExlS3BwQewx0/nX/aN+BHif4J/tMeNv2YLyG8uL7wf4mm0iPaOb4K+2KVFAziVSjqvUhx3r+r6W40fR7S41vWtQitrawt2lu7i6l8uKKNAWaRmJwoABJJ6AV8R+EvhN+x7+2N+0nd/t9+E/hHHY39pqlvHYeIdYs1EmtzWUeyK/SMu3lJt8kRuQshECMVXvzujShrY97LM9zfL1OGFqcqlbm0TvbbdM/Dn9pT9gn4w/sfa54c8NfHfSY9N1XXdGtNX/se3LO1tbyyMhilcrt81duWVCwUnBIORXkvjDU7ueYTrO7rE+Cpw2wcDHTkcfh6Cv6Df29Pgf8ADL9uv4S6h8L/ABvbm2vbRiPD+vwp/pGl3A6SA5G5WwAyZAde4IVh+Lv7VP8AwTp+PX7Ivhy88V+P9U0K/wBIhufIs7zT79g127nCgI6Ag4+Y9gAetc1ryuz9Zybi7La2RrBz5oVn8cr35mneLUUlprblXba/vHingC10nWfGtimqzRxWSTCa/mccRxINznsOgP44r6j+A37eHx28PnxMfAPjmXQtLn1JraSGGJcm33MEX58hQE8kcYOSea+RPD+o+IdVuJ9Ajigt7S42i7WGPLOiESbSx5xlVPGORXqXw30l5NL1LRICRPctEWQjkPdXUYXP/bOBGH+/WGIvHW9v8j6vhmnhc1xFONXDxqU1KU2pxVpTUWkknfSKu1fV3lppc/ZP/ggp+2X8QfiT4s8dfsufFDxbqGsT6fosHibQrnULhpZlQ3D2t2hZiTsLfZXC8AM8h/ir9FL1YxEDGQSXBbaOv+Ffht/wQy+JEc//AAVj0/TNFvAsF58ONR02Tac+cqZuRnHXPlq34Cv3Rli8qNvOTcxJGduB+ld2Ck5YdXPx/wAUMLhMPxliHhklCbukkktG46JabxK0VubydRExjBky2eox7/nT9XtDAioZmIXO1RyD2qncXcVo/wAi7c4OWPIHtVW+vpnAYFiOfnbuRXWfnqNRrmS4i+xRx5HXeeh/OsbWNP8ANj8sOo2rgLk4P40qao6yRwyblwu4vnkE9vSo729GHD5LFSVLDOf8/wBKBao5W+ilt5JbWSIY2EKT83H9PSsS9ixL9oyEUdAF4A//AF1013BFGjhjIqs/zNjgjAx+Vcx4okuIgEgJJDHPXbj6/Q/rTsK5z91dmIyWahdsbn5hwMHmsc3trExUxIv17+/FP1i5HkytIDjljgkn1rBTKKBHKQpGQFjzx+dNMQ3TpI7e2W28w5kYAYbrntXZeHg0LAxTRhidxLAnaM46Z+leaWty015HDJtDLJySPp/9eu48P6osEQjeN8gAAls4GCfxqSzv01GEGOBpQuRkEEYb/CtfSJLXaHhB34zjPTPY/wCe1cXY6naiMi4UhlI2lu59P/rVuaZrF20ipDGp5HBzg9sdaBnbQy3TxgQzKWDZCqMfqK07WG/llK3KlAfusGyCOP8A69YNhfS+SPkwzKcbSDzXRWF7EIllYEsq42n8KANPTZPKlCsmF3jBPAJx9PWrF5udmQkeWFBUZxz+NZ0epYynlAMz5Qg9Tj+lWLa5WO22zSklh2GaBdSdYnRRERjABU5q2uAfKaTJ4+X2rNGolpNu7PpnBwfXj3q28iwZmIJXYANvb6/pSGW5pIwCrcggHZv5HWiJ0KmbaQDgD0x+H0qhbOpUXClXZl4J7npg+1WbmaS8025ghRBM0DKoJ4DEHH4UCPCP+CgfiXwDdfsua/N8T/GN3pHgfT2jv/GMthATPqunwP5j6emGBRZ2WONjyWVmQAb9w/FCH/gsp8ZvCPxZ1TxV8JvCGmaV4SluEg0zwU8eIYLJVK8yLyJiQjFgCCWbjAAr9lfEEnwT/at+Cd34R8UQ2Xibwpr+nGG6to7xgk67v78bBlKunYhlK9Qa/PH9o3/g3p8DzWF74g/Zb+M1/Y3bOZLfw74wjWaFup8tLqIBkA6Dcjn1PeuGVScndn6NwjPhDDRqUc4hLmk0k9bRS9Nbt6N20W1tT4k8U/8ABSn9rvUfjncfHHwp8VbzSC0my28Ohln0+O2DblheNlCynnlyobk429K4b9sH9tf4zfti+J7XVviVqtvHb2MQSz0fSomjtIHwA8oVizFm9ydoJA6mtH9oX9iH9qL9mzUJrT4l/CTUFtULBdX0yM3VpIox83mJnYDkY3hT7V4izoj+ZKwIz9wd/akm29T77EZfwuo06uXRjp9pNv8APr99ulmdH8PNMhjdGaHNzfzrFbRnj5Nw3sfQcYz7H0re0jxo2k+EvFXxAgl2NqOpLaaOQcchSiN/wCLnP94L61y1jqc2naXNdKd+o36m3tEHWMMNuR6fKTj3xXo0f7En7YfxHttI8JeCP2ffEz2FrCTFLc2BtY5pHPzSbpigwcDBPG0CueUPaT1/q39Jfeeys6pZFglKDSlGMuXp781yxb84xlOT7e6vN+6f8EB/En9i/wDBSnwr4sdgiTSTaZC79AbiCSGNfxHFf0XTNeIZYmlCsRhWODkentX4zf8ABGf/AII/ftM+AvjRoHxl+O2m6f4S0vw/rceqfYJNUgury+lgVjDGqwO6xqHO5i7A4UjaSeP2UuLyGCHzz8z4OxSfwFduFv73r+iPyDjzE5diamDeHqKc1SftGtlKVSc0r97S17bGZIJbnEd2iMYxid145x2x0H+NVdRulA8pAGwcEg8Yp0t/JK6oinvvwcEZqC5W1JTEm2SQ/cJ645NdZ8CNVxMwY8kLkZGDjFUdQv7u4lOY2yp2gAjJ4HIqZpvKkkUr95eWJ5B9f5Vl3N5LbSkkYI4XPPGaBEdxdNO2xZyQrdCen5VzviSSdmkCyAlgeNx4A9Kt6i8AYyJMe/OcjPp7VzOs63dQSSlZAFOQBkZPfINAjDvdUsZfNiiGxlU4VvUdevXmuXvtVvprgyBmOf8AY/xArX1TUIbiRiVUl1OQq8/SuYvdage4JituAAPnwD/9egYzQZYIbqOacrkjCj+Vddpd7b4VN5GWwCW4NeX6XrUk8qSQyqGj+6BgA89+56mujsdTuTdi4V2AZuA6kKMfX/PFBR6dY3kJYRBfMbbncxJxzXQaZdTvIgW35AIyR/hXnulXMkMQne7h3kAEt6e3Nbml+JPJXalwxU4O4AHAPAznr0/WgD0fStRZ0wHAZThcHB610FjqZ2kyYyEAx715pomvafMztaTHLMDIqHkHHQ88f/Wrp9K16FdN5vGMaknLD+ZoA7fTrmGSAXJGW2nHI4JFTLcQXLi1gcg4yTj9PbmsKx1l2gUxttXbjlc4zVmz1oeXukw24hV+Ugnt+X6UAbkVu0SB3mAIPIJ6A5q6s08iLbswf0HUVgQa7azAWztGu0Z2LJnb16Vw37Sf7UfhT9mn4T6h8T9ZjMws1KWka5PmytnHA5OMEke2OpFTKSjG7HGLk7I6v43fHj4W/s1/D65+LHxf8TNpeiWLpFcXKWM05jZ2wo2RKzDJOMkY55Ir4/8A2rv+C437Mun/ALP+tJ+z34w1W78T6jY3Nnptx/Ystt9jdoX23IedVjcK+0YDFgWB2tjaeg8NfszeLvjjaH4l/tqeOtYurvUsXsXgWx1FrO20uLIdYJHhIeaQxgglHRY3ynzcNXhH7V/7AXw4+JP7Q3hb4N/s3eIr3Sbq30y68Ua1b6pqTXFhbW1vOq2au8oaQGaVwoZ3kGEf5G24rO9V62t+ZtGNFOzd/wAj55/aE/Zb/bG/4JI/CPwP+1n+zX8T7/UfC/i/QrKX4gW1zp5e0stVkUuokgkUFIHEgRJMK4dSrMpeMHY+Fn/Bw1odxpkOmfHf4H6jZ3QAWfUPCl0k8TerCC4ZGTr08xjx1r6a/ZD8e6T4L8b/APDGXxU8PQal8MPiSbzQ7jwdqkY+z6BrYhnmNtEnSG2u4oLv9wh2Q3NqTEEWZUX81v8Agq3/AMEwfiD/AME+fiW+veGbS51r4Ya5dN/wjmtMN72LHLfYblgPllUA7XwFlUbhgh1TnlC65o7H32S18pzpLB5jG1VL3ZrRyXnbdr53Wvc/Qrwl/wAFUf2APHyJD/wv6xtXmT95BrmnXNpszxhmljCD3wxHvimeJtH/AOCYnxanbxDqerfBrXmlfzPtEuo6bKzsCVyW3Z65HX1Ffhu93ZyjMMmxu6kc1nXMdsJfNSZVI98YqFFs9HFcIRox9phK2nqv+Af0AeBG/wCCenwW1eLx3Y+HPglocunRiVNUht9Kt3QZXYRKMHqq4OeT9axdU/bp/ZN1bxQyX37TXhK61DVZVSzh0zUhcquSflzCGWMdssQOme1fhb4L07RdT163j1e5hZWljVRcEeUgz8zbcYY4z1zz6V+q/wAIvgn/AMEsPj5+w83xQ1j4Xaj4L8VaXfr4dU+Htcu7ufWdVSLev2W2vHljczF4gYgoKYkIKqoepUU58t9T57Mskx+CwbxdRpwul8S5tevLe9uj3tdXSufpB+zv8WdG8J+KdM+FXiPRNUsp9Wtftmj6pcWimz1QMkrhYZFZjkLDKx3hfujn503e16lf2r3hLXKAFOEPU9K/L7/glL8K9T+AH7ROrfDb9ovVdft/EWk+GlvfBGk3mstPpdvb3AxLJChYhZx+9jxn5N1wgGcs36DXfizS47g3iSmSSJ9rjeeB9OnpXZQUVB2PkMRdz1OpurqO3ZZ47jgNgh1znGPTtWJq95cXUi35Ypsctt3gbex75PGfpXMap8SoHjka1mDMBwmRkcHH+fasWX4oQCGSS4uAHHQZ6f5/nW5gkegya39ptI5EfL5BPv8An7msrXNYiimGQGYffQEdeOK4L/hZYuEJhvAETJcxnoO2P8/lWbq3jwTxsBMWKHHOA2fTg0BZHW6zrMJhIEgV8nAVjn8a5HVtUiYsguC2cjJ6g/WuUuvEcyPJdSXjLu+ZhznHPUE4rD1bxjDIxhS7ZJ+QF5OSR146DjqcDtQFjf1zXLdDLsmJZV+ZFxnBBwa4LUNYt5Lkt9tzwPmHf1zz1zmm6r4mWWJ1N0GKnbKhj3EEDof05rkr7xHG8weJYiCgOc8HPPHHSgRNBqWqbvKuLo2clxHm3TaI3UnnODjPGeOvHIHStzT9Y1Tw3B9s1nWpJojKgMs3yiN3baFXkkgsygDsD9a8u0/xM2p6u2p6l4ls7iSIAW8ctkA4wfmZsQqQ23C5wRhe55rX1m/8L+J4bP8A4SnWryG4tbtZreW0uAI/MUcMFwdvUjJA6nBA6q5pynrNn8QG02JbPXNdSGRZlhRhMoUORnbhuS2O3XmtE+PrKwg+0DxU67VAaQAMpGCcBVAGcZI/HrXhl+dB1sQwXGo7YY3Cxz+XE4k4B2MMfPx8vIGPUdQ7SbOwg1pbdNSmsrSxtWGnK08e4K4XI4jbb90HLszDpuwTU8z6IOU9+svje4KHTvOliZm3XjhY0hA69W3buR1HIyc9BUmlfHbTTqMunJK1zdROwubaKLcYH6EMMAsR3yWryjTtctdOiuLay1qFXuJvMF3dgPE4XBztjRCw4K/e574qV/CWk6ldW2ra94fF8tsixQ7bNkjQDsIy8nLYwQ4IbjcCKLza2Cx73pX7SK2ISMmSQBeUhyQB2HygqDjJAznjp1xs+EP2ib3xXqf2C30+dYVfm4iZgnHHXHzenp1rwPR18CeGNSGrafoulaZewjMk1rbL5wywyJHCFTk8leAc4I5xV9/H9hBulR7sIXQQTrNsUqSBtBULI2eOctjr3yS8uwuU+lNR+Imm+HLgT37TbrlDtORlgoycZOeBk59Afavnf9u3x7o3iuT4fXTSy/2VofxB0671h2KuojF1AwJUnBAVXZg2PlU9qiHiHTr+xGl6lOIhGjAeTfvFMo6FWZD5ncgCRhjIOB1rK8YwfBLxB4RvPDviGQb57d41v765luFQtyRvbcCCR0BbP1OaipzSg0kaUmoTTZ6n8f8AWPid4p+CXiLTvgh4mW38Qz6dPDpVxdyxxiK8GQQrbSiNuBwRkZwWIB5+W/2Vf2af+CiHgez1T4kap+1zpvhvxT4nWNtUuNU8LR+IbxfI3LFC085Ij2biQqAqA4wSOlfw9+0xoHgqKXwR4v1ax8Tx2MD21nPH4rW2vFg2sqxSwyzRJMAHPzlgxwuRkHNr4j/8FBvCOrifw14Mex0Se6Plx6r4k16KWeMZLK0UMM8kfmK7yESSPhcjcr4AqFVju/u6lqnUjorW7nBeD9O+OS/8FDvA/hXxx+0R/wAJtev8SBdX1zaeGYLM35sbUT3E7mJjHEI2aSEBACzZznewH6Q/E3VPh/8AEXw3qfwr+L/hjS9d0LWAbXUdLvlWZJlOCMgLlGHykEcq3zAggGvkv4DeKv2dPhf4dE+jePPD2ra9NGXuNf1CIyG3EmDJHHKx3uWIDMRje3zYP8PprftPaZripYxaxp7pcNutLIyxs0jY4m2FisS/xAEE+nXNaUlLk95CnUaqqUHtaz226o/FL9qz9lNPAfxH8dweBtDvotO8LeJby1vbSSGVk06Hev2VWuCuGMgMqqWx/wAe55ORXifjTwRqHgPxfqPgnU9WspbzTLt7eeXT9Rju7V3U4JjmiJSVc9GUkHqCRX6W/wDBXn4MeJvjP42sviX8FtZ8HiWz0Z7bW4tPnitNRvXbdlpC7lJo/L+VQNrE7hhhtx+bOteE9Y0bWF03VLO4iupYFlEEnl52uMqwGQcEYIz2+tR7Poj7HLOKqkal8c3KNt1FX+bVn+Y7wzKsEsdnf7ZVaQbv3YwBn86/Rv8A4Ic+FbT4hfFbVfGF0ukX9n4QsyLKyuQstxZz3BVDNArnbDkJseTBJDBcY5HwHb/De2h0NL7WfGmk2DSqWS3lcyMT2EhRSqAjOB8xz1xX1P8AsKfGfwV+ydo2ra7ZpceLNV1u0WKLS0ihisLdlcMsrSxyyzS8bl2eSnDH5hnIy9mo1OZ7o9DOONHjsoqZbhqf7udryn8Vk01bXTVbt7N6H6PfHO43/tyfC/8A4RtzHqVpYanJqkbySyOls4QRh1ZRtU4uCMKByeK9f0/SPECRT3tmriGcjadhUIMfNiPbgcgcA+pr4R+Bn7Rmh6b451D4teOVub/xJq6/vyNFeG2solHywwK3IA6DIPAJO4sxPr9x+174Q1LTLqZj5cV/KRdQ3FtE3nuRwXDAY4GPlA6dsc7U+a7k1ufntRqyinse96R4x03Xy9vps80txauYbuGG4jbZtOCrAMcEev8Ahzl62LV7k2a3r2+UOyRtxDAcg4IUfXB7kcYrynXv2jLSw02xtba+0mGe4SN0WDTY/mRuFBCpk8c8tn0z1rAtv2sdTv8AxK+nxbUdJSzTzxRgSOoxkBFwpwOScng81qm+piet2upalozvNbJujlIESD5mbA+Y7cZUZzjDH8OlVdQ8QazNaPd3IuLR0HKzWvCkYOFfAyO/4/hXD6n+0trflrLo2rw30SnabW2ACRZ5OWIJf07c+nSs7UvH3iXxLcWt9LpTiCNFkhv4ZkiaA4JxuKhmHsQQfQ07gddf+INa1/SZp7O/RMbhFdMgXzNuQcDBLdCO3eudvtRsXgZb7xNbMJwquN6xzIAcBXGTgnIOGHfoOBXJaj8T9an1OfWNa+zfZY23SSWszyXDkEAO8ihSMY3HnoAPWub0uy+Gnhi3TxbBqXl2t/eyiJ3jCo02Tv8AMRy4YkNgtjcwPPFJOXYLHo9wzT6idKW8EjPCXhjF065UgYG5eD8wON3I5A45rHmSEOY7pkd043SSkkjtyTyMd+9Um8Y6jYSDWNM1axvFXcyJc7BGMgn92UAyMH+LP881NZ1zTry88+++FOlam7IP9Kk0lHJHpnPOOarcR5pBr/iDyvsMuoiWObeBLauqgtjBR2ZVxgDHygnkjPJNT6JqNhFCuq6pcAW6PH5n2xf3W5R2DfNI3JycYFee2mvXJ1BYzojeaqeXFaRzBEjwOc4UEEEkkdeDnHONvTfF6yuLXUdUuvMG9HurdfNjtwCBuVQBnPT7oUdRk00kVqejafrMuoWHnQQQ2tssmN0EjCTaxO1QTny1OcAYGecBsHFiPWtNsIhLNf8A2S2Eu3y5flkeQdSqse2fv845Gc/LXl9/q1xpUkvh+2mvLhbdTJu0Q/61zHwSxA3qvIyBxhufmqxqGqvZtbeHNRE+oJFbF473Tr3c4iLFyjqVIOCTnBBGeScYqtBas9OPiaeGE3aanNEsv+ojW5CSOnJDtISCFz/dznHbrVq28bavo2nLBPqTReazTCBroiIRsAQ7EAs7MScZbgeucDyG88XS695On2t3A08dsvkXKSCQpCOglRSpO0YBIztHtyF1nxTr3i23lbVZNON3p9okUl3YSGSGdVO1Q4ZcKecZ3HkDCnINLQLHs7eLIba5TSrq9he92sRE10EhtjjovTLDnIPyjgc4zV3/AITXSW1CdLfxHbXbJbqLi+GX4HBEYHQHKjtkAZxkivE11jX9bu/Kl0aazuLUYfVo5gsEwwoDksQQeDygyc/cPWtjRBqd3DPfajBe6bcQoVluI4wTcFlyI1XcDk7T/CV6EgUgPUYPFQl0y6gtU+z2VrOgMEK7zKz5wzlUxtGOGIABPHOTVy68a3ENgmrC6lhEgKwQRKyqqqAvPKgHnI6k8E96828Ox6rBas89vPazI+Y3t4mkZz1YOuSGXHX+HnHpRf3MmnrPe6dr9xLdXIBfTrO1doQBnmSNhIQB2TjGSRtotcNj1211fXNYtbXT9PtLm/e8iSR54bZppGQqM8IDkAHB6ZPHYCpx8Pbm5vxod78JdXhtVlbcw0KUxTueQSViORnHJYBefpXp/wCx7a6bB8DLHXNP0/yZ9UuLie7WBWYHbM0a5D5K4VOmRjn1Ndta/wDCwEkWK0u7REkG7zPNZtg80ncY9vJ8vggtwT170+UnmPmr/hTWo6xeMur/AAx1QC1LG2hbQZli+XOE+7jBOTjO1jwc55yNX+CUt/ZXkekfCbXIrq6k/wBJmGkXcbmPK8LuBGc9RjJA44zX1tbjxTFqxS/u45raSRhFAo+RIwDtYZG4uSFyS2PmOACoLV7O48cSadLYXmm2FvMLFjFeC5klXzQCARGY1wM8435wMc9aOUOY+GPF37Gdz4l062Ww+GOqxvGpFxJJosxdssWAJCkkbSBnt7dK4S5/4J56tpnieXVNL+FGqvE85ULBokyIAVwM/LkD3P4c1+kUUvjrUNHu0tLeygmaExwz/bHlIkYYDbWiGAOuOfoaZeWXjzTbaTz/ABQt3czqqwRTWgUW/OGkyhBfjOF4GVAyKLC5j87PDP7Afi7S1mj1L4eaqqSlPJlXSpnRMHJyY0bbnI6/jjt28f7K3iOy0yBrT4e6ukloNqf8SWbY3f8AhQ/NknHbgDivtPUrbx//AGRZ2OneIo7a9+0lp7xbYSkw7T8pXKgNuIywwMLnAzgQa1F8U7awtLDQvEcE+oLI7XF88Ih3qegCqrjI5ycgH86dgufMWkfB7xZp13Fqk3wl1tjIrtPZPp8rwMGJBAZYyVOMHHXn25SL4W+MtGnntofhhrTQTIPNsjpk4OwcjbL5Y+cYzg4HbknFfTTWnxHaO006TxYkN1H5pvLm1slm87JHl4GF4Ck5P885qDV7L4rwGwjg8U2QlRGjvwi5V33cOoVGZcD+Fj17Glyj5rnypc/C/wCIlxJJZ3fw614QREtYyHQblZR83oxUNx79eRxnOZB8Lfizf3qzD4c6uGhXi6TSJE3HtlJEB6Zyec54yeK+xLx/iVYGzilksbtzDALiLzzERKrEyNhYicOpAGQpUjOOeI7mXxlDaSxy3cDXDt+5RptqR5mJPWJjxGQoJQ5K52jNHKg5j5GT4d/FbTmYL8PvEXkyyKPJis38hiSchgY/MQDt8vGTyKSTwF8Rll+y3PgvxPJAE3RBNImOzODwVTdj2OOpJFfWM1l8TU0q6DahbpdO0RsXluVlCKCd+5lgTAIK4HlnBzzyALHh228aW+ny/wDCU6nFdTSThonWXaBFt/65KSdw9gfXiiwXPkGDwZ8U4POmHgXXR5qsCItCuATkdWyvueh5yc9BWJrHhr4n2C/Y0+EviG7sJAGNu+jXjbHAwG74bBPIHRuvavs7w5p/xCiuFuPEGpC5AhYMYrtDEzBcZC+QrAZP3TJkYxlqzY4fiRZlludVhSb7NID5zLIofYQhCLBGRhiCSWbgEYJIYFkK7Pii68L/ABrSxgtIfg94lmtVJBtf7Gu18g56htozwTyQAPerVz4I+KE8xMnwb8VyFQF3w6O+04HUbeOevBPXrnNfZ2mHx9Jq9pHqmsWc1nBvWWGO3ZZJxglWyzEIwO35Rxwx7hV2bqdZpMs0se0bQjkkgfgf6CjlGpn/2Q==",
                    "file_type": "jpg"
                }
            }
        }
        username = "pratik@dummy.com"
        self.assertRaises(Exception, OrganizationService().add_organization_draft, payload, username)

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    def test_submit_org_for_approval(self, ipfs_mock):
        org_service = OrganizationService()
        payload = {
            "org_id": "",
            "org_uuid": "",
            "org_name": "dummy_org",
            "org_type": "individual",
            "metadata_ipfs_hash": "",
            "description": "that is the dummy org for testcases",
            "short_description": "that is the short description",
            "url": "https://dummy.dummy",
            "contacts": [],
            "assets": {}
        }
        username = "pratik@dummy.com"
        response_org = org_service.add_organization_draft(payload, username)
        test_org_id = response_org["org_uuid"]
        payload["org_uuid"] = test_org_id
        org_service.submit_org_for_approval(payload, "dummy@snet.io")

        orgs = self.org_repo.get_org_with_status(test_org_id, "APPROVAL_PENDING")
        if len(orgs) == 0:
            assert False
        else:
            self.assertEqual(orgs[0].OrganizationReviewWorkflow.updated_by, "dummy@snet.io")

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    def test_publish_org_ipfs(self, ipfs_mock):
        test_org_id = uuid4().hex
        username = "dummy@snet.io"
        self.org_repo.add_org_with_status(DomainOrganization(
            "dummy_org", "org_id", test_org_id, "organization", username,
            "that is the dummy org for testcases", "that is the short description", "dummy.com", [], {}, "",
            duns_no=12345678, groups=[], addresses=[]),
            "APPROVED", username)
        response = OrganizationService().publish_org_to_ipfs(test_org_id, username)
        self.assertEqual(response["metadata_ipfs_hash"], "Q3E12")

        orgs = self.org_repo.get_org_with_status(test_org_id, "APPROVED")
        if len(orgs) == 0:
            assert False
        else:
            self.assertEqual(orgs[0].OrganizationReviewWorkflow.updated_by, username)
            self.assertEqual(orgs[0].Organization.metadata_ipfs_hash, response["metadata_ipfs_hash"])

    def test_add_group(self):
        """ adding new group without existing draft """
        test_org_id = uuid4().hex
        username = "dummy@snet.io"
        organization = DomainOrganization(
            "dummy_org", "org_id", test_org_id, "organization", username,
            "that is the dummy org for testcases", "that is the short description", "dummy.com", [], {}, "",
            duns_no=12345678, groups=[], addresses=[])
        organization.add_group(DomainGroup(
            name="my-group",
            group_id="group_id",
            payment_address="0x123",
            payment_config={},
            status=''
        ))
        self.org_repo.add_org_with_status(organization, OrganizationStatus.PUBLISHED.value, username)
        payload = [
            {
                "name": "my-group",
                "id": "",
                "payment_address": "0x123",
                "payment_config": {
                    "payment_expiration_threshold": 40320,
                    "payment_channel_storage_type": "etcd",
                    "payment_channel_storage_client": {
                        "connection_timeout": "5s",
                        "request_timeout": "3s",
                        "endpoints": [
                            "http://127.0.0.1:2379"
                        ]
                    }
                }
            },
            {
                "name": "group-123",
                "id": "",
                "payment_address": "0x123",
                "payment_config": {
                    "payment_expiration_threshold": 40320,
                    "payment_channel_storage_type": "etcd",
                    "payment_channel_storage_client": {
                        "connection_timeout": "5s",
                        "request_timeout": "3s",
                        "endpoints": [
                            "http://127.0.0.1:2379"
                        ]
                    }
                }
            }
        ]
        OrganizationService().add_group(payload, test_org_id, username)

    def test_add_group_two(self):
        """ adding new group without existing draft """
        test_org_id = uuid4().hex
        username = "dummy@snet.io"
        organization = DomainOrganization(
            "dummy_org", "org_id", test_org_id, "organization", username,
            "that is the dummy org for testcases", "that is the short description", "dummy.com", [], {}, "",
            duns_no=12345678, groups=[], addresses=[])
        organization.add_group(DomainGroup(
            name="my-group",
            group_id="group_id",
            payment_address="0x123",
            payment_config={},
            status=''
        ))
        self.org_repo.add_org_with_status(organization, OrganizationStatus.DRAFT.value, username)
        payload = [
            {
                "name": "my-group",
                "id": "",
                "payment_address": "0x123",
                "payment_config": {
                    "payment_expiration_threshold": 40320,
                    "payment_channel_storage_type": "etcd",
                    "payment_channel_storage_client": {
                        "connection_timeout": "5s",
                        "request_timeout": "3s",
                        "endpoints": [
                            "http://127.0.0.1:2379"
                        ]
                    }
                }
            },
            {
                "name": "group-123",
                "id": "",
                "payment_address": "0x123",
                "payment_config": {
                    "payment_expiration_threshold": 40320,
                    "payment_channel_storage_type": "etcd",
                    "payment_channel_storage_client": {
                        "connection_timeout": "5s",
                        "request_timeout": "3s",
                        "endpoints": [
                            "http://127.0.0.1:2379"
                        ]
                    }
                }
            }
        ]
        OrganizationService().add_group(payload, test_org_id, username)

    def test_save_transaction(self):
        test_org_uuid = uuid4().hex
        org_id = "org_id"
        org_name = "dummmy_org"
        username = "dummy@snet.io"
        organization = DomainOrganization(
            org_name, org_id, test_org_uuid, "organization", username,
            "that is the dummy org for testcases", "that is the short description", "dummy.com", [], {}, "QWE",
            duns_no=12345678, groups=[], addresses=[])
        self.org_repo.add_org_with_status(organization, OrganizationStatus.APPROVED.value, username)
        OrganizationService().save_transaction_hash_for_publish_org(test_org_uuid, "0x98765", "0x123", username)
        org_db_models = self.org_repo.get_org_with_status(test_org_uuid, OrganizationStatus.PUBLISH_IN_PROGRESS.value)
        if len(org_db_models) == 0:
            assert False
        else:
            org = org_db_models[0]
            self.assertEqual(org_id, org.Organization.org_id)
            self.assertEqual(org_name, org.Organization.name)

    def tearDown(self):
        self.org_repo.session.query(Organization).delete()
        self.org_repo.session.query(OrganizationReviewWorkflow).delete()
        self.org_repo.session.query(OrganizationHistory).delete()
        self.org_repo.session.commit()
