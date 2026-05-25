
from app.domain.services.cep import Cep
from app.domain.services.cpf import Cpf
from app.exeception.domain.complaint_domain_execption import ComplaintNotFound, ImageNotFound
from app.infrastructure.build.complaint_build import ComplaintBuild
from app.infrastructure.repository.complaint_repository import ComplaintRepository
from app.models.models import Address, Complaint
from sqlalchemy.orm import Session
from minio import Minio
from minio.error import S3Error
from app.main import bucket_name, minio_client
class ComplaintService:
    def __init__(self, session: Session):
        self.complaint_repository = ComplaintRepository(session=session)
        self.cep_service = Cep(),
        self.db = session

    def list_comaplaint_service(self, complaintFilterSchema):
        
        query = (
                    ComplaintBuild(self.db.query(Complaint))
                    .filter_category(complaintFilterSchema.category)
                    .filter_status(complaintFilterSchema.status)
                    .filter_by_pagination(complaintFilterSchema.page,complaintFilterSchema.limit)
                    .build()
                )

        complaints = query.all()

        if not complaints:
            raise ComplaintNotFound("Nenhuma denúncia encontrada.")

        return complaints

    def create_comaplaint_service(self, complaintSchema):

        # Buscar cep da denúncia
        address = self.cep_service.search_cep(complaintSchema.cep)
         
        if not self.__verify_image_exist(minio_client=minio_client, bucket=bucket_name, object_name=complaintSchema.image_path):
            raise ImageNotFound("Imagem não encotrada na base de arquivos.")
        
        create_complaint = Complaint(
                cpf=complaintSchema.cpf,
                category=complaintSchema.category,
                longitude=address["longitude"],
                latitude=address["latitude"],
                image_url=complaintSchema.image_path,
                description=complaintSchema.description
            )

        new_complaint = self.complaint_repository.register_repository(create_complaint)

        create_address = Address(
            complaint_id= new_complaint.id,
            city=address["cidade"]["nome"],
            state=address["estado"]["sigla"],
            street=address["logradouro"],
            neighborhood=address["bairro"]
        ) 

        self.complaint_repository.register_repository(create_address)

        return {
            "id": new_complaint.id,
            "status": new_complaint.status,
            "created_at": new_complaint.created_at
        }




    def __verify_image_exist(self,minio_client: Minio, bucket: str, object_name: str) -> bool:

        try:
            # Tenta obter informações do objeto sem baixar o conteúdo
            estatisticas = minio_client.stat_object(bucket, object_name)
            return True
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return False
            raise
