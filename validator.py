import os.path
import sqlite3

DATABASE_FILE = "cardtype.db"
MAX_CARD_LENGTH = 19
MIN_CARD_LENGTH = 8


class CCNumber:
    card_number: list[int]

    def __init__(self, card_number):
        self.card_number = [int(ch) for ch in str(card_number)]

    def __len__(self):
        length = len(self.card_number)
        return length

    def __str__(self):
        return "".join([str(x) for x in self.card_number])

    def __repr__(self):
        return "Card Number: {}".format(self.card_number)

    def validate(self):
        rev_card = self.card_number[::-1]
        return (
            sum(rev_card[0::2])
            + sum(sum(divmod(d * 2, 10)) for d in rev_card[1::2])
        ) % 10 == 0


class SingletonBase(object):
    def __new__(type):
        if not "_the_instance" in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance


class CCProcessor:
    type: str

    def __str__(self):
        return self.type

    def __repr__(self):
        return "The card type is: {}".format(self.__str__())

    def validate(self, card_number: CCNumber, cvv: str, expiration: str):
        return False

    def validate_simple(self):
        return True


class CCMasterCard(CCProcessor, SingletonBase):
    type = "Mastercard"

    def validate(self, card_number: CCNumber, cvv: str, expiration: str):
        return True


class CCVisa(CCProcessor, SingletonBase):
    type = "Visa"

    def validate(self, card_number: CCNumber, cvv: str, expiration: str):
        return True


class CCDiscovery(CCProcessor, SingletonBase):
    type = "Discovery"

    def validate(self, card_number: CCNumber, cvv: str, expiration: str):
        return True


class CCUnknown(CCProcessor):
    type = "Unknown"

    def validate(self, card_number: CCNumber, cvv: str, expiration: str):
        return False


class CCProcessorExtractor:
    db: sqlite3.Connection
    card_number: CCNumber

    def __init__(self, card_number: CCNumber):
        self.db = sqlite3.connect(DATABASE_FILE)
        self.card_number = card_number

    def __del__(self):
        self.db.close()

    def __find_type(self):
        cursor = self.db.cursor()
        card_number_str = str(self.card_number)
        cursor.execute(
            "SELECT cctt.card_name,cctt.processor_digits FROM CreditCardProcessor  as cctt WHERE (? LIKE cctt.processor_digits || '%') ORDER BY LENGTH(cctt.processor_digits) DESC LIMIT 1",
            (card_number_str,),
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        return None

    def find(self):
        CCProcessor = self.__find_type()
        match CCProcessor:
            case "VISA":
                return CCVisa()
            case "MASTERCARD":
                return CCMasterCard()
            case "DISCOVERY":
                return CCDiscovery()
            case _:
                return CCUnknown()


class CCValidator:
    card_number: CCNumber
    CCProcessor: CCProcessor

    def __init__(self, card_number):
        self.card_number = CCNumber(card_number)
        type_extractor = CCProcessorExtractor(self.card_number)
        self.CCProcessor = type_extractor.find()

    def validate(self):
        return self.card_number.validate() and self.CCProcessor.validate(
            self.card_number, "445", "hi"
        )

    def validate_verbose(self):
        is_valid = self.validate()
        val_card_str = "Card number validity for {}: {} \n".format(
            self.card_number,
            self.card_number.validate(),
        )
        val_card_type_str = "Card type validity for {}: {} \n".format(
            self.CCProcessor,
            self.CCProcessor.validate(self.card_number, "445", "hi"),
        )
        card_is_valid_str = "Card is valid: {}\n".format(is_valid)
        print(val_card_str + val_card_type_str + card_is_valid_str)
        return self.validate()


def create_card_type_tb(conn):
    conn.execute(
        """CREATE TABLE IF NOT EXISTS CreditCardProcessor 
         (id            INT PRIMARY KEY    NOT NULL,
         card_name      TEXT    NOT NULL,
         processor_digits    CHAR(6),
         min_length     INT NOT NULL,
         max_length     INT NOT NULL);"""
    )
    conn.commit()


def load_card_type_db(conn):
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (1, 'MASTERCARD', '51',16,16)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (2, 'MASTERCARD', '52',16,16)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (3, 'MASTERCARD', '53',16,16)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (4, 'MASTERCARD', '54',16,16)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (5, 'MASTERCARD', '55',16,16)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (6, 'MASTERCARD', '22',16,16)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (7, 'MASTERCARD', '23',16,16)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (8, 'MASTERCARD', '24',16,16)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (9, 'MASTERCARD', '25',16,16)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (10, 'MASTERCARD', '26',16,16)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (11, 'MASTERCARD', '27',16,16)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (15, 'VISA', '4',13,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (16, 'DISCOVERY', '60',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (17, 'DISCOVERY', '6011',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (18, 'DISCOVERY', '644',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (19, 'DISCOVERY', '645',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (20, 'DISCOVERY', '646',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (21, 'DISCOVERY', '647',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (22, 'DISCOVERY', '648',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (23, 'DISCOVERY', '649',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (24, 'DISCOVERY', '65',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (25, 'DISCOVERY', '6221',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (26, 'DISCOVERY', '6222',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (27, 'DISCOVERY', '6223',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (28, 'DISCOVERY', '6224',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (29, 'DISCOVERY', '6225',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (30, 'DISCOVERY', '6226',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (31, 'DISCOVERY', '6227',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (32, 'DISCOVERY', '6228',16,19)"
    )
    conn.execute(
        "INSERT INTO CreditCardProcessor  (id,card_name,processor_digits,min_length,max_length) VALUES (33, 'DISCOVERY', '6229',16,19)"
    )
    conn.commit()


def create_db():
    if not os.path.isfile(DATABASE_FILE):
        conn = sqlite3.connect(DATABASE_FILE)
        create_card_type_tb(conn)
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
