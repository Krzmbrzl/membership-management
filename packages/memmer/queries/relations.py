# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import exists
from sqlalchemy import or_
from sqlalchemy import select

from memmer.orm import Member, Relation


def are_related(session: Session, first: Member, second: Member) -> bool:
    """Checks whether the given two members are related"""
    result = session.query(
        exists(Relation).where(
            or_(
                (Relation.first_id == first.id) & (Relation.second_id == second.id),
                (Relation.second_id == first.id) & (Relation.first_id == second.id),
            )
        )
    ).scalar()

    return result


def get_relatives(session: Session, member: Member) -> List[Member]:
    """Gets a list of members that are related to the given one"""
    relations = session.scalars(select(Relation).where(or_(Relation.first_id == member.id, Relation.second_id == member.id))).all()

    relatedMembers: List[Member] = []

    for currentRelation in relations:
        first = session.scalars(select(Member).where(Member.id == currentRelation.first_id)).first()
        second = session.scalars(select(Member).where(Member.id == currentRelation.second_id)).first()

        assert first != None
        assert second != None

        if member != first and not first in relatedMembers:
            relatedMembers.append(first)
        if member != second and not second in relatedMembers:
            relatedMembers.append(second)
        
    return relatedMembers



def make_relation(session: Session, first: Member, second: Member) -> None:
    """Ensures that the given two members are stored as being related to each other"""
    if not are_related(session, first, second):
        relation = Relation(first_id=first.id, second_id=second.id)
        session.add(relation)


def drop_relation(session: Session, first: Member, second: Member) -> None:
    """Removes the relationship between the two members"""
    relation = session.scalars(
        select(Relation).where(
            or_(
                (Relation.first_id == first.id) & (Relation.second_id == second.id),
                (Relation.second_id == first.id) & (Relation.first_id == second.id),
            )
        )
    ).first()

    if not relation is None:
        session.delete(relation)
