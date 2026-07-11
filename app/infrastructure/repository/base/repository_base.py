from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from abc import ABC
import logging

class RepostiroyBase(ABC):

    def __init__(self, session: Session, model):
        self.db = session
        self.model = model

    # repositorio de visualização
    def get_repository(self):

        data = self.db.query(self.model)
        return data
    
    # repositorio de filtro
    def filter_repository(self, filters: list, port_logic_and: bool = True):

        query = self.db.query(self.model)
        try:
            if port_logic_and:
                data = query.filter(and_(*filters))
            else:
                data = query.filter(or_(*filters))
        except:
            logging.error("Error ao filtrar objeto")

        return data
    
     # repositorio de filtro join
    def filter_join_repository(self,relation, filters: list, port_logic_and: bool = True):

        query = self.db.query(self.model).join(relation)

        try:
            if port_logic_and:
                data = query.filter(and_(*filters))
            else:
                data = query.filter(or_(*filters))
        except:
            logging.error("Error ao filtrar objeto")

        return data
    
    # repositorio de registro
    def register_repository(self, new_object):
        self.db.add(new_object)
        self.db.commit()
        self.db.refresh(new_object)

        logging.info("Objeto registrado com sucesso")

        return new_object

    # repositorio de salvar
    def save_repository(self, object_saved):
        self.db.commit()
        self.db.refresh(object_saved)

        logging.info("Dados salvos com sucesso")

        return object_saved

    
    def search_for_ids(self, ids: list[int]):
         return self.db.query(self.model).filter(self.model.id.in_(ids)).all()
    