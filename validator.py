import os.path
import sqlite3

DATABASE_FILE = "cardtype.db"
MAX_CARD_LENGTH = 19
MIN_CARD_LENGTH = 8


class CardNumber:
    card_number: list[int]

    def __init__(self, card_number):
        self.card_number = [int(ch) for ch in str(card_number)]

    def __len__(self):
        length = len(self.card_number)
        return length

    def __str__(self):
        as_str = map(str, self.card_number)
        return "".join(as_str)

    def __repr__(self):
        return "Card Number: {}".format(self.card_number)

    def get_number(self):
        return self.card_number

    def get_first_two_digits(self):
        return self.card_number[0:2]

    def validate(self):
        rev_card = self.card_number[::-1]
        return (
            sum(rev_card[0::2])
            + sum(sum(divmod(d * 2, 10)) for d in rev_card[1::2])
        ) % 10 == 0

    def length(self):
        return int(len(self.card_number))


class SingletonBase(object):
    def __new__(type):
        if not "_the_instance" in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance


class CCType:
    type: str

    # def __init__(self, card_number: CardNumber):
    #     self.card_number = card_number

    def __str__(self):
        return self.type

    def __repr__(self):
        return "The card type is: {}".format(self.__str__())

    def validate(self, card_number: CardNumber, cvv: str, expiration: str):
        return False


class CCMasterCard(CCType, SingletonBase):
    type = "Mastercard"

    def validate(self, card_number: CardNumber, cvv: str, expiration: str):
        return True


class CCVisa(CCType, SingletonBase):
    type = "Visa"

    def validate(self, card_number: CardNumber, cvv: str, expiration: str):
        return True


class CCDiscovery(CCType, SingletonBase):
    type = "Discovery"

    def validate(self, card_number: CardNumber, cvv: str, expiration: str):
        return True


class CCUnknown(CCType):
    type = "Unknown"

    def validate(self, card_number: CardNumber, cvv: str, expiration: str):
        return False


class CCTypeExtractor:
    db: sqlite3.Connection
    card_number: CardNumber

    def __init__(self, card_number: CardNumber):
        self.db = sqlite3.connect(DATABASE_FILE)
        self.card_number = card_number

    def __del__(self):
        self.db.close()

    def __find_type(self):
        cursor = self.db.cursor()
        card_nums = self.card_number.get_first_two_digits()
        card_length = len(self.card_number)
        first_digits = str(card_nums[0]) + str(card_nums[1])
        cursor.execute(
            "SELECT card_name, min_length, max_length FROM CREDIT_CARD_TYPE WHERE type_digits == ? AND ? BETWEEN min_length AND max_length;",
            (
                first_digits,
                card_length,
            ),
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        return None

    def find(self):
        cctype = self.__find_type()
        match cctype:
            case "VISA":
                return CCVisa()
            case "MASTERCARD":
                return CCMasterCard()
            case "DISCOVERY":
                return CCDiscovery()
            case _:
                return CCUnknown()


class CCValidator:
    card_number: CardNumber
    cctype: CCType

    def __init__(self, card_number):
        self.card_number = CardNumber(card_number)
        type_extractor = CCTypeExtractor(self.card_number)
        self.cctype = type_extractor.find()

    def validate(self):
        return self.card_number.validate() and self.cctype.validate(
            self.card_number, "445", "hi"
        )

    def validate_verbose(self):
        is_valid = self.validate()
        val_card_str = "Card number validity for {}: {} \n".format(
            self.card_number,
            self.card_number.validate(),
        )
        val_card_type_str = "Card type validity for {}: {} \n".format(
            self.cctype,
            self.cctype.validate(self.card_number, "445", "hi"),
        )
        card_is_valid_str = "Card is valid: {}\n".format(is_valid)
        print(val_card_str + val_card_type_str + card_is_valid_str)
        return self.validate()


def create_card_type_tb(conn):
    conn.execute(
        """CREATE TABLE IF NOT EXISTS CREDIT_CARD_TYPE
         (id            INT PRIMARY KEY    NOT NULL,
         card_name      TEXT    NOT NULL,
         type_digits    CHAR(2),
         min_length     INT NOT NULL,
         max_length     INT NOT NULL);"""
    )
    conn.commit()


def create_card_length_tb(conn):
    conn.execute(
        """CREATE TABLE IF NOT EXISTS CREDIT_CARD_TYPE_LENGTH
         (
         card_name      TEXT  PRIMARY KEY  NOT NULL,
         min_length     INT NOT NULL,
         max_length     INT NOT NULL
         );"""
    )
    conn.commit()


def load_card_length_db(conn):
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE_LENGTH (card_name,min_length,max_length) VALUES ('MASTERCARD',16,16)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE_LENGTH (card_name,min_length,max_length) VALUES ('VISA',13,19)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE_LENGTH (card_name,min_length,max_length) VALUES ('DISCOVERY',16,19)"
    )
    conn.commit()


def load_card_type_db(conn):
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE (id,card_name,type_digits,min_length,max_length) VALUES (1, 'MASTERCARD', '51',16,16)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE (id,card_name,type_digits,min_length,max_length) VALUES (2, 'MASTERCARD', '52',16,16)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE (id,card_name,type_digits,min_length,max_length) VALUES (3, 'MASTERCARD', '53',16,16)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE (id,card_name,type_digits,min_length,max_length) VALUES (4, 'MASTERCARD', '54',16,16)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE (id,card_name,type_digits,min_length,max_length) VALUES (5, 'MASTERCARD', '55',16,16)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE (id,card_name,type_digits,min_length,max_length) VALUES (6, 'VISA', '40',13,19)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE (id,card_name,type_digits,min_length,max_length) VALUES (7, 'VISA', '41',13,19)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE (id,card_name,type_digits,min_length,max_length) VALUES (8, 'VISA', '42',13,19)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE (id,card_name,type_digits,min_length,max_length) VALUES (9, 'VISA', '43',13,19)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE (id,card_name,type_digits,min_length,max_length) VALUES (10, 'VISA', '44',13,19)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE (id,card_name,type_digits,min_length,max_length) VALUES (11, 'VISA', '45',13,19)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE (id,card_name,type_digits,min_length,max_length) VALUES (12, 'VISA', '46',13,19)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE (id,card_name,type_digits,min_length,max_length) VALUES (13, 'VISA', '47',13,19)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE (id,card_name,type_digits,min_length,max_length) VALUES (14, 'VISA', '48',13,19)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE (id,card_name,type_digits,min_length,max_length) VALUES (15, 'VISA', '49',13,19)"
    )
    conn.execute(
        "INSERT INTO CREDIT_CARD_TYPE (id,card_name,type_digits,min_length,max_length) VALUES (16, 'DISCOVERY', '60',16,19)"
    )
    conn.commit()


def create_db():
    if not os.path.isfile(DATABASE_FILE):
        conn = sqlite3.connect(DATABASE_FILE)
        create_card_type_tb(conn)
        create_card_length_tb(conn)
        load_card_length_db(conn)
        load_card_type_db(conn)
        conn.close()


if __name__ == "__main__":
    create_db()
    visa_cards = [
        "4556223722828538",
        "4556801884892960",
        "4556440052496518",
        "4556034365549095",
        "4485550342104189",
    ]
    master_cards = [
        "5446375636262476",
        "5392129049466842",
        "5374108134954583",
        "5413611702414735",
        "5467680644140240",
    ]
    discovery_cards = [
        "6011619174162728",
        "6011721731954694",
        "6011386836937836",
        "6011945354231102",
        "6011552675304467",
    ]

    all_true_cards = []
    all_true_cards.extend(visa_cards)
    all_true_cards.extend(master_cards)
    all_true_cards.extend(discovery_cards)

    for card in all_true_cards:
        card_validator = CCValidator(card)
        isValid = card_validator.validate_verbose()

    false_card_number = "4222222222222222"
    false_validator = CCValidator(false_card_number)
    valid = false_validator.validate_verbose()
