
from app.domain.enums.report_status_enums import ReportStatusEnum
from app.domain.services.cep import Cep
from app.domain.services.cpf import Cpf
from app.exeception.domain.complaint_domain_execption import ComplaintNotFound, ComplaintStatusInvalid, ImageNotFound
from app.exeception.domain.user_domain_exeception import AuthNotAuthorized
from app.infrastructure.build.complaint_build import ComplaintBuild
from app.infrastructure.repository.complaint_repository import ComplaintRepository
from app.models.models import Address, Complaint, User
from sqlalchemy.orm import Session
from minio import Minio
from minio.error import S3Error
from app.main import bucket_name, minio_client
class ComplaintService:
    def __init__(self, session: Session):
        self.complaint_repository = ComplaintRepository(session=session)
        self.cep_service = Cep(),
        self.db = session

    def list_comaplaint_service(self, complaintFilterSchema, user_loggin: User):
        
        if not user_loggin.validate_is_admin():
            raise AuthNotAuthorized("Usuário não tem permissão para acessar esse conteúdo.",403)

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

    def details_complaint_service(self, complaint_id: int, user_loggin: User):

        if not user_loggin.validate_is_admin():
            raise AuthNotAuthorized("Usuário não tem permissão para acessar esse conteúdo.",403)
        
        details = self.complaint_repository.filter_repository([Complaint.id == complaint_id]).first()

        if not details:
            raise ComplaintNotFound("Denúncia não encontrada.")

        return details

    def alter_status_service(self,complaint_id: int, status: ReportStatusEnum, user_loggin: User):
            
        if not user_loggin.validate_is_admin():
            raise AuthNotAuthorized("Usuário não tem permissão para alterar esse conteúdo.",403)

        complaint = self.complaint_repository.search_complaint(complaint_id)

        if not complaint:
            raise ComplaintNotFound("Denúncia não encontrada na base de dados.")


        match status:
            case ReportStatusEnum.ANALYSING.name:
                complaint.ansalysing()
            
            case ReportStatusEnum.RESOLVED.name:
                complaint.resolved()
            
            case ReportStatusEnum.REJECTED.name:
                complaint.rejected()
        
            case _:
                raise ComplaintStatusInvalid("Status inválido")

        altered_status = self.complaint_repository.save_repository(object_saved=complaint)

        return {
            "id": altered_status.id,
            "status": altered_status.status,
            "updated_at": altered_status.updated_at
        }
           

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
