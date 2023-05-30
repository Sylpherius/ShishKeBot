from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Base(DeclarativeBase):
    pass


class Kebot(Base):
    __tablename__ = "kebot"

    guild_id: Mapped[str] = mapped_column(primary_key=True)
    channel_id: Mapped[str]

    def __repr__(self) -> str:
        return f"Kebot(guild_id={self.guild_id!r}, channel_id={self.channel_id!r})"


class KebotUsers(Base):
    __tablename__ = "kebot_users"

    user_id: Mapped[str] = mapped_column(primary_key=True)
    level: Mapped[int]
    total_cards: Mapped[int]
    battle_team: Mapped[str]
    primosticks: Mapped[int]
    daily: Mapped[int]

    def __repr__(self) -> str:
        return f"KebotUsers(user_id={self.user_id!r}, level={self.level!r}, total_cards={self.total_cards!r}, " \
               f"battle_team={self.battle_team!r}, primosticks={self.primosticks!r}, daily={self.daily!r})"


class KebotUserInv(Base):
    __tablename__ = "kebot_user_inv"

    user_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    card_name: Mapped[str]
    card_quantity: Mapped[int]

    def __repr__(self) -> str:
        return f"KebotUserInv(user_id={self.user_id!r}, card_name={self.card_name!r}, card_quantity={self.card_quantity!r})"


class KebotCards(Base):
    __tablename__ = "kebot_cards"

    card_name: Mapped[str] = mapped_column(primary_key=True)
    image: Mapped[str]
    card_rarity: Mapped[str]
    top_energy: Mapped[int]
    card_type: Mapped[str]
    card_series: Mapped[str]
    description: Mapped[str]

    def __repr__(self) -> str:
        return f"KebotCards(card_name={self.card_name!r}, image={self.iamge!r}, card_rarity={self.card_rarity!r}, " \
               f"top_energy={self.top_energy!r}, card_type={self.card_type!r}, card_series={self.card_series!r}, description={self.description!r})"


class KebotBattle(Base):
    __tablename__ = "kebot_battle"

    user_id: Mapped[str] = mapped_column(primary_key=True)
    battle_id: Mapped[str]
    battle_team: Mapped[str]
    selected_card: Mapped[int]
    grave: Mapped[str]
    score: Mapped[str]

    def __repr__(self) -> str:
        return f"KebotBattle(user_id={self.user_id!r}, battle_id={self.battle_id!r}, battle_team={self.battle_team!r}, " \
               f"selected_card={self.selected_card!r}, grave={self.grave!r}, score={self.score!r})"
