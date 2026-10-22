from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# URL Koneksi Utama ke MySQL XAMPP (Database: eduaps_db)
MYSQL_URL = "mysql+pymysql://root:@localhost/eduaps_db"
SQLITE_FALLBACK_URL = "sqlite:///./eduaps_fallback.db"

try:
    engine = create_engine(MYSQL_URL, echo=False, pool_pre_ping=True)
    with engine.connect() as conn:
        pass
    ACTIVE_DB_ENGINE = "MySQL (eduaps_db)"
except Exception:
    engine = create_engine(
        SQLITE_FALLBACK_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    ACTIVE_DB_ENGINE = "SQLite Fallback (eduaps_fallback.db)"

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# =====================================================================
# 1. TABEL RUANG BELAJAR (Sequence: Mengakses Ruang Belajar)
# =====================================================================
class Materi(Base):
    __tablename__ = "materi"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    kode = Column(String(50), unique=True, nullable=False)  # Materi 1 .. Materi 6
    minggu = Column(String(100), nullable=False)
    judul = Column(String(255), nullable=False)
    ringkasan = Column(String(500), nullable=True)
    konten_html = Column(Text, nullable=False)


# =====================================================================
# 2. TABEL RUANG TRYOUT & HASIL UJIAN (Sequence: Taking a Tryout)
# =====================================================================
class SoalTryout(Base):
    __tablename__ = "soal_tryout"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    kategori = Column(String(50), index=True, nullable=False)  # Materi 1..6 atau Soal UAS
    pertanyaan = Column(Text, nullable=False)
    opsi_a = Column(String(255), nullable=False)
    opsi_b = Column(String(255), nullable=False)
    opsi_c = Column(String(255), nullable=False)
    opsi_d = Column(String(255), nullable=False)
    kunci_index = Column(Integer, nullable=False)  # 0=A, 1=B, 2=C, 3=D
    pembahasan = Column(Text, nullable=True)


class HasilUjian(Base):
    __tablename__ = "hasil_ujian"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nama_user = Column(String(100), nullable=False, default="Mahasiswa")
    kategori_tryout = Column(String(50), nullable=False)  # Materi 1..6 atau Soal UAS
    jumlah_benar = Column(Integer, nullable=False)
    total_soal = Column(Integer, nullable=False)
    skor = Column(Integer, nullable=False)
    waktu_selesai = Column(DateTime, default=datetime.now)


# =====================================================================
# 3. TABEL FORUM TANYA JAWAB (Sequence: Using a Q&A Forum)
# =====================================================================
class Pertanyaan(Base):
    __tablename__ = "pertanyaan"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nama_user = Column(String(100), nullable=False)
    isi_pertanyaan = Column(Text, nullable=False)
    waktu_dibuat = Column(DateTime, default=datetime.now)

    jawaban_list = relationship(
        "Jawaban",
        back_populates="pertanyaan",
        cascade="all, delete-orphan",
    )


class Jawaban(Base):
    __tablename__ = "jawaban"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pertanyaan_id = Column(
        Integer, ForeignKey("pertanyaan.id", ondelete="CASCADE"), nullable=False
    )
    nama_user = Column(String(100), nullable=False)
    isi_jawaban = Column(Text, nullable=False)
    waktu_dijawab = Column(DateTime, default=datetime.now)

    pertanyaan = relationship("Pertanyaan", back_populates="jawaban_list")


# =====================================================================
# 4. TABEL PENYIMPANAN FILE UML (Sequence: UML Maker Application)
# =====================================================================
class FileUML(Base):
    __tablename__ = "file_uml"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    judul_diagram = Column(String(150), nullable=False)
    tipe_diagram = Column(String(50), nullable=False)  # usecase / sequence / activity
    format_file = Column(String(20), nullable=False, default="svg")
    data_json = Column(Text, nullable=True)
    konten_svg = Column(Text, nullable=False)
    waktu_disimpan = Column(DateTime, default=datetime.now)


def init_db():
    Base.metadata.create_all(bind=engine)
