from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import os

from database import (
    SessionLocal,
    ACTIVE_DB_ENGINE,
    Materi,
    SoalTryout,
    HasilUjian,
    Pertanyaan,
    Jawaban,
    FileUML,
    init_db,
)

# Inisialisasi tabel database otomatis jika belum ada
init_db()

app = FastAPI(
    title="EduAPS Backend System",
    description="API Sistem Ruang Belajar, Ruang Tryout & Grading System, Forum Tanya Jawab, dan Aplikasi Pembuat UML",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== DATA AWAL (SEEDER DATABASE) ====================
SEED_MATERI = [
    {
        "id": 1,
        "kode": "Materi 1",
        "minggu": "Pertemuan 1",
        "judul": "Pengantar Pengembangan Sistem & Konsep Dasar SI",
        "ringkasan": "Konsep dasar sistem, subsistem, 7 karakteristik sistem, komponen CBIS, klasifikasi SI (TPS, MIS, DSS, Expert System), serta siklus pengembangan sistem.",
        "konten_html": """
            <p><strong>1. Pengertian Sistem &amp; Subsistem:</strong> Sistem adalah sekumpulan elemen atau objek yang saling berelasi, berinteraksi, dan bekerja sama sebagai satu kesatuan untuk mencapai tujuan tertentu (Murdick &amp; Ross, 1993; McLeod, 1995). Sistem terdiri dari <em>Input &rarr; Pengolahan (Transformasi) &rarr; Output</em> dengan mekanisme kontrol dan umpan balik (<em>feedback</em>). Sistem yang kompleks tersusun atas beberapa <strong>subsistem</strong>.</p>
            <div class="bg-blue-50 p-4 rounded-xl border border-blue-100 my-3">
                <h4 class="font-bold text-slate-800 mb-1">7 Karakteristik Sistem:</h4>
                <p class="text-sm">Batasan (<em>Boundary</em>), Lingkungan (<em>Environment</em>), Masukan (<em>Input</em>), Keluaran (<em>Output</em>), Komponen (<em>Component</em>), Penghubung (<em>Interface</em>), dan Penyimpanan (<em>Storage</em>).</p>
            </div>
            <p><strong>2. Komponen &amp; Klasifikasi Sistem Informasi:</strong> Menurut Stair (1992), CBIS terdiri dari <em>Hardware, Software, Database, Telekomunikasi, dan Manusia</em>. Burch &amp; Grudnitski (1986) membaginya menjadi 6 blok bangunan (Masukan, Model, Keluaran, Teknologi, Basis Data, Kendali). Klasifikasi SI meliputi <strong>TPS</strong> (Transaction Processing System), <strong>MIS</strong> (Management Information System), <strong>DSS</strong> (Decision Support System), dan <strong>Expert System</strong>.</p>
            <p><strong>3. Pengembangan Sistem:</strong> Dilakukan untuk menyusun sistem baru guna menggantikan atau memperbaiki sistem lama karena adanya masalah, pertumbuhan organisasi, meraih peluang bisnis, atau kebijakan. Tujuannya meningkatkan <strong>Throughput</strong> (jumlah pekerjaan dalam satu waktu) dan mempercepat <strong>Response Time</strong>.</p>
            <p><strong>4. Prinsip &amp; Alat Perancangan:</strong> Sistem dikembangkan untuk manajemen, merupakan investasi modal besar, memerlukan SDM terdidik, memiliki dokumentasi, serta menggunakan alat perancangan seperti <em>HIPO, DFD, Structured Chart, SADT, Warnier/Orr, Jackson's Diagram</em>, dan manajemen proyek <strong>CPM &amp; PERT</strong>.</p>
        """,
    },
    {
        "id": 2,
        "kode": "Materi 2",
        "minggu": "Pertemuan 2",
        "judul": "Investigasi Kebutuhan Sistem & Rekayasa Kebutuhan",
        "ringkasan": "Tahapan Preliminary Investigation, kerangka PIECES, keputusan Go or No Go, 7 langkah Requirement Engineering, serta kebutuhan Fungsional vs Non-Fungsional.",
        "konten_html": """
            <p><strong>1. Preliminary Investigation (Investigasi Awal):</strong> Tahap awal analisis pengembangan sistem (biasa selesai dalam 2–3 hari). Terdiri dari 5 tahap: (1) <em>List Problems, Opportunities, and Directives</em> (dikategorikan dengan kerangka <strong>PIECES</strong>), (2) <em>Negotiate Preliminary Scope</em>, (3) <em>Assess Project Worth</em> (menghasilkan keputusan <strong>"Go or No Go"</strong>), (4) <em>Plan the Project</em>, dan (5) <em>Present the Project and Plan</em> (menghasilkan <em>Project Charter</em>).</p>
            <p><strong>2. Identifikasi Masalah:</strong> Meliputi 3 langkah berurutan: (1) Mengidentifikasi <strong>penyebab masalah</strong>, (2) Mengidentifikasi <strong>titik keputusan</strong> (kondisi yang menyebabkan sesuatu terjadi), dan (3) Mengidentifikasi <strong>personil kunci</strong> (pihak yang terlibat langsung/tidak langsung).</p>
            <div class="bg-amber-50 p-4 rounded-xl border border-amber-200 my-3">
                <h4 class="font-bold text-slate-800 mb-1">7 Kegiatan Rekayasa Kebutuhan (Requirement Engineering):</h4>
                <p class="text-sm">1. <em>Inception</em> (Pengenalan Permasalahan) &bull; 2. <em>Elicitation</em> (Penggalian Kebutuhan) &bull; 3. <em>Elaboration</em> (Elaborasi) &bull; 4. <em>Negotiation</em> (Negosiasi) &bull; 5. <em>Specification</em> (Spesifikasi) &bull; 6. <em>Validation</em> (Validasi) &bull; 7. <em>Requirements Management</em>.</p>
            </div>
            <p><strong>3. Kebutuhan Fungsional vs Non-Fungsional:</strong></p>
            <ul class="list-disc pl-5 space-y-1 text-sm">
                <li><strong>Kebutuhan Fungsional:</strong> Layanan spesifik yang harus disediakan sistem dan bagaimana sistem bereaksi terhadap input (contoh: Sistem dapat menghitung nilai tryout dan menampilkan Hasil Ujian).</li>
                <li><strong>Kebutuhan Non-Fungsional:</strong> Batasan kualitas layanan yang meliputi <em>Kebutuhan Produk</em> (kinerja, waktu respon &le; 10 detik, efisiensi memori), <em>Kebutuhan Organisasi</em>, dan <em>Kebutuhan Eksternal</em>.</li>
            </ul>
        """,
    },
    {
        "id": 3,
        "kode": "Materi 3",
        "minggu": "Pertemuan 3",
        "judul": "Systems Development Life Cycle (SDLC) & Metodologi",
        "ringkasan": "Empat fase utama SDLC (Planning, Analysis, Design, Implementation) beserta deliverables dan perbandingan metode Waterfall, Prototype, Spiral, RAD, dan Scrum.",
        "konten_html": """
            <p><strong>1. Konsep Dasar SDLC:</strong> Proses mengembangkan atau mengubah suatu sistem perangkat lunak menggunakan model dan metodologi teruji. Empat fase utama beserta keluarannya (<em>Deliverables</em>) adalah:</p>
            <ul class="list-disc pl-5 space-y-1 text-sm">
                <li><strong>Planning (Why build?):</strong> Mengidentifikasi nilai bisnis &amp; analisis kelayakan (Teknis, Ekonomis, Organisasi) &rarr; menghasilkan <em>System Proposal</em>.</li>
                <li><strong>Analysis (Who, what, when, where?):</strong> Mengumpulkan kebutuhan &amp; mempelajari sistem saat ini &rarr; menghasilkan <em>Business Process Model / System Specification</em>.</li>
                <li><strong>Design (How will the system work?):</strong> Desain program (UML), desain UI, dan desain data (ERD) &rarr; menghasilkan <em>System Specification</em>.</li>
                <li><strong>Implementation:</strong> Konstruksi sistem, Testing (Unit, Integration, System, User Acceptance Test), dan Instalasi &rarr; menghasilkan <em>New System</em>.</li>
            </ul>
            <div class="bg-purple-50 p-4 rounded-xl border border-purple-100 my-3">
                <h4 class="font-bold text-slate-800 mb-1">5 Metode Pengembangan SDLC:</h4>
                <p class="text-sm"><strong>1. Waterfall (Linear Sequential):</strong> Bertahap dan berurutan, cocok jika kebutuhan sudah jelas di awal.<br>
                <strong>2. Prototype:</strong> Membuat <em>mock-up</em> cepat agar user bisa mengevaluasi tampilan/fungsi lebih awal.<br>
                <strong>3. Spiral (Barry Boehm):</strong> Menggabungkan prototyping dan waterfall dengan penekanan utama pada <strong>Analisis Risiko (Risk Analysis)</strong> di setiap putaran.<br>
                <strong>4. RAD (Rapid Application Development):</strong> Pembangunan cepat (60–90 hari) melalui 4 fase: <em>Requirements Planning, User Design (JAD), Construction, Cutover</em>.<br>
                <strong>5. Scrum (Agile):</strong> Menangani produk kompleks melalui <em>Backlog, Sprints (~30 hari), Daily Scrum (15 menit), dan Demo</em> bersama <em>Product Owner, Scrum Master, dan Tim Scrum</em>.</p>
            </div>
        """,
    },
    {
        "id": 4,
        "kode": "Materi 4",
        "minggu": "Pertemuan 4",
        "judul": "Unified Modeling Language (UML) & Use Case Diagram",
        "ringkasan": "Sejarah penyatuan UML (Booch, Rumbaugh, Jacobson), 4 View UML, komponen Use Case Diagram, serta relasi <<include>>, <<extend>>, dan Generalization.",
        "konten_html": """
            <p><strong>1. Sejarah &amp; Konsep UML:</strong> UML (<em>Unified Modeling Language</em>) adalah bahasa pemodelan visual standar untuk sistem berorientasi objek yang menyatukan metode <strong>G. Booch (OOD)</strong>, <strong>J. Rumbaugh (OMT)</strong>, dan <strong>I. Jacobson (OOSE)</strong> pada tahun 1995. UML memiliki 4 macam <em>view</em>: <em>Use Case View, Logical View, Physical View, dan Component View</em>.</p>
            <p><strong>2. Konsep Dasar Use Case Diagram:</strong> Memodelkan "apa" yang dilakukan sistem (fungsionalitas dari sudut pandang pengguna), bukan "bagaimana" cara kerjanya secara teknis. Terdiri dari 4 elemen utama (Dennis et al., 2015): <strong>Actor</strong>, <strong>Use Case</strong>, <strong>Subject/System Boundary</strong>, dan <strong>Relationship</strong>.</p>
            <div class="bg-emerald-50 p-4 rounded-xl border border-emerald-200 my-3">
                <h4 class="font-bold text-slate-800 mb-1">3 Relasi Penting Antar Use Case:</h4>
                <ul class="list-disc pl-5 text-sm space-y-1">
                    <li><strong>&laquo;include&raquo; (Wajib/Required):</strong> Menunjukkan bahwa suatu use case mutlak membutuhkan use case lain sebagai bagian dari eksekusinya (contoh pada EduAPS: setiap tryout <em>Materi 1..6 &amp; Soal UAS &rarr; &laquo;include&raquo; &rarr; Hasil Ujian</em>).</li>
                    <li><strong>&laquo;extend&raquo; (Opsional):</strong> Menunjukkan use case tambahan yang berjalan pada kondisi tertentu sementara use case utama dapat berdiri sendiri (contoh: <em>Input Jawaban / Jawab Pertanyaan &rarr; &laquo;extend&raquo; &rarr; Forum Tanya Jawab</em>). Arah panah menuju ke <strong>use case utama</strong>.</li>
                    <li><strong>Generalization (Spesialisasi):</strong> Mewarisi sifat dari use case induk yang lebih umum (contoh: <em>Materi 1..6</em> terhadap <em>Ruang Belajar</em>).</li>
                </ul>
            </div>
        """,
    },
    {
        "id": 5,
        "kode": "Materi 5",
        "minggu": "Pertemuan 5",
        "judul": "Analisis, Desain, dan Implementasi Sistem",
        "ringkasan": "Empat langkah analisis sistem (Identify, Understand, Analyze, Report), Conceptual vs Physical Design, pengujian error, serta 4 pendekatan konversi sistem.",
        "konten_html": """
            <p><strong>1. Empat Langkah Analisis Sistem:</strong></p>
            <ol class="list-decimal pl-5 text-sm space-y-1">
                <li><strong>Identify (Identifikasi Masalah):</strong> Mencari penyebab masalah, titik keputusan (dengan <em>paperwork/form flowchart</em>), dan personil kunci.</li>
                <li><strong>Understand (Memahami Kerja Sistem):</strong> Penelitian terinci (<em>detailed survey</em>) melalui wawancara, observasi, kuesioner, dan pengambilan sampel.</li>
                <li><strong>Analyze (Menganalisis Sistem):</strong> Mengevaluasi distribusi beban kerja, keandalan, dokumen, laporan, dan teknologi berdasarkan kriteria <em>relevance, capacity, efficiency, timeliness, accessibility, flexibility, accuracy, reliability, security, economy, simplicity</em>.</li>
                <li><strong>Report (Laporan Hasil Analisis):</strong> Diserahkan ke <em>Steering Committee</em> (Panitia Pengarah) dan manajemen.</li>
            </ol>
            <p><strong>2. Desain Sistem:</strong> Terbagi menjadi <strong>Desain Sistem Secara Umum (Conceptual Design)</strong> yang meliputi desain Output, Input, Database, Kontrol, dan Teknologi untuk dikomunikasikan ke user, serta <strong>Desain Sistem Terinci (Physical Design)</strong> untuk programmer.</p>
            <div class="bg-blue-50 p-4 rounded-xl border border-blue-100 my-3">
                <h4 class="font-bold text-slate-800 mb-1">Tahap Implementasi &amp; Konversi Sistem:</h4>
                <p class="text-sm">Meliputi penyusunan anggaran &amp; penjadwalan (<strong>Gantt Chart</strong>), pemilihan &amp; pelatihan personil, instalasi HW/SW, pemrograman &amp; pengetesan (menguji <em>Syntax Error, Run-Time Error, Logical Error</em> melalui Unit, Integration, &amp; Validation Test), serta <strong>4 Pendekatan Konversi Sistem</strong>: Konversi Langsung (<em>Direct</em>), Paralel (<em>Parallel</em>), Percontohan (<em>Pilot</em>), dan Bertahap (<em>Phased</em>).</p>
            </div>
        """,
    },
    {
        "id": 6,
        "kode": "Materi 6",
        "minggu": "Pertemuan 6",
        "judul": "Pemeliharaan Sistem (System Maintenance)",
        "ringkasan": "Hukum evolusi perangkat lunak, indikator MTBF, 4 tipe pemeliharaan (Corrective, Adaptive, Perfective, Preventive), serta CASE Tools (Forward & Reverse Engineering).",
        "konten_html": """
            <p><strong>1. Konsep &amp; Hukum Evolusi Perangkat Lunak:</strong> Pemeliharaan adalah fase terpanjang dalam SDLC yang dimulai sejak sistem beroperasi. Menurut <em>Laws of Software Evolution</em>, kompleksitas software terus meningkat dan perubahan tidak pernah berhenti. Efektivitas pemeliharaan diukur menggunakan <strong>MTBF (Mean Time Between Failures)</strong>—semakin tinggi nilai MTBF, semakin baik keandalan sistem.</p>
            <div class="bg-amber-50 p-4 rounded-xl border border-amber-200 my-3">
                <h4 class="font-bold text-slate-800 mb-1">4 Tipe Pemeliharaan Sistem:</h4>
                <ul class="list-disc pl-5 text-sm space-y-1">
                    <li><strong>Corrective Maintenance (Korektif):</strong> Memperbaiki <em>bug</em> logika, <em>error</em> program, atau kerusakan saat sistem berjalan.</li>
                    <li><strong>Adaptive Maintenance (Adaptif):</strong> Menyesuaikan sistem terhadap perubahan lingkungan luar (contoh: pembaruan OS/browser atau regulasi pajak baru).</li>
                    <li><strong>Perfective Maintenance (Penyempurnaan):</strong> Meningkatkan kinerja atau menambah fitur baru sesuai kebutuhan pengguna.</li>
                    <li><strong>Preventive Maintenance (Preventif):</strong> Inspeksi periodik untuk mencegah kerusakan di masa depan (contoh: <em>backup</em> rutin, <em>patch</em> keamanan).</li>
                </ul>
            </div>
            <p><strong>2. Struktur Organisasi &amp; CASE Tools:</strong> Pengelolaan personil pemeliharaan dibagi menjadi 3 struktur: <em>Terpisah (Separate)</em>, <em>Kombinasi (Combined)</em>, dan <em>Fungsional (Functional)</em>. Alat bantu <strong>CASE (Computer-Aided Software Engineering)</strong> mendukung <strong>Forward Engineering</strong>, <strong>Reverse Engineering</strong> (menganalisis kode sistem lama untuk membuat dokumentasi), <strong>Reengineering</strong>, dan <strong>Restructuring</strong>.</p>
        """,
    },
]

SEED_SOAL = [
    # Materi 1
    {
        "kategori": "Materi 1",
        "pertanyaan": "Ukuran kinerja sistem yang menunjukkan jumlah pekerjaan yang dapat dilakukan pada suatu saat tertentu disebut...",
        "opsi_a": "Response Time",
        "opsi_b": "Throughput",
        "opsi_c": "Boundary",
        "opsi_d": "Confirmability",
        "kunci_index": 1,
        "pembahasan": "Throughput adalah jumlah pekerjaan yang dapat diselesaikan dalam satu unit waktu, sedangkan Response Time adalah waktu tunda tanggapan sistem.",
    },
    {
        "kategori": "Materi 1",
        "pertanyaan": "Sistem informasi yang mengotomasi penanganan data aktivitas bisnis dan transaksi rutin harian disebut...",
        "opsi_a": "Expert System",
        "opsi_b": "Decision Support System (DSS)",
        "opsi_c": "Transaction Processing System (TPS)",
        "opsi_d": "Executive Information System",
        "kunci_index": 2,
        "pembahasan": "TPS (Transaction Processing System) memproses data transaksi operasional harian secara rutin.",
    },
    {
        "kategori": "Materi 1",
        "pertanyaan": "Berikut ini yang BUKAN merupakan kriteria pemeriksaan keabsahan data sumber informasi adalah...",
        "opsi_a": "Credibility (Derajat Kepercayaan)",
        "opsi_b": "Transferability (Keteralihan)",
        "opsi_c": "Profitability (Tingkat Keuntungan)",
        "opsi_d": "Confirmability (Kepastian)",
        "kunci_index": 2,
        "pembahasan": "Empat kriteria keabsahan data kualitatif adalah Credibility, Transferability, Dependability, dan Confirmability.",
    },
    # Materi 2
    {
        "kategori": "Materi 2",
        "pertanyaan": "Tahapan dalam Preliminary Investigation yang menghasilkan keputusan 'Go or No Go' (apakah proyek layak dilanjutkan atau dibatalkan) adalah...",
        "opsi_a": "Negotiate Preliminary Scope",
        "opsi_b": "Assess Project Worth",
        "opsi_c": "List Problems & Directives",
        "opsi_d": "Present the Project",
        "kunci_index": 1,
        "pembahasan": "Assess Project Worth menilai kelayakan ekonomis dan manfaat proyek untuk memutuskan Go atau No Go.",
    },
    {
        "kategori": "Materi 2",
        "pertanyaan": "Kerangka kerja yang digunakan untuk mengkategorikan Problems, Opportunities, dan Directives adalah...",
        "opsi_a": "SDLC",
        "opsi_b": "HIPO",
        "opsi_c": "PIECES",
        "opsi_d": "SCRUM",
        "kunci_index": 2,
        "pembahasan": "PIECES (Performance, Information, Economy, Control, Efficiency, Service) digunakan untuk mengklasifikasikan masalah sistem.",
    },
    {
        "kategori": "Materi 2",
        "pertanyaan": "'Proses menampilkan artikel berlangsung tidak lebih dari 10 detik dan ukuran program maksimal 100 MB' merupakan contoh dari...",
        "opsi_a": "Kebutuhan Fungsional",
        "opsi_b": "Kebutuhan Non-Fungsional",
        "opsi_c": "Titik Keputusan",
        "opsi_d": "Inisiasi Proyek",
        "kunci_index": 1,
        "pembahasan": "Batasan kecepatan waktu respon dan kapasitas memori termasuk Kebutuhan Non-Fungsional (Kebutuhan Produk).",
    },
    # Materi 3
    {
        "kategori": "Materi 3",
        "pertanyaan": "Model SDLC yang diperkenalkan oleh Barry Boehm dan sangat menekankan pada Analisis Risiko (Risk Analysis) di setiap iterasinya adalah...",
        "opsi_a": "Model Waterfall",
        "opsi_b": "Model Prototype",
        "opsi_c": "Model Spiral",
        "opsi_d": "Model RAD",
        "kunci_index": 2,
        "pembahasan": "Model Spiral menggabungkan pendekatan iteratif dengan evaluasi Analisis Risiko di setiap putaran.",
    },
    {
        "kategori": "Materi 3",
        "pertanyaan": "Dalam metode Agile Scrum, pihak yang bertanggung jawab menentukan spesifikasi bisnis dan menyusun daftar kebutuhan awal (Product Backlog) adalah...",
        "opsi_a": "Scrum Master",
        "opsi_b": "Product Owner",
        "opsi_c": "Database Administrator",
        "opsi_d": "System Tester",
        "kunci_index": 1,
        "pembahasan": "Product Owner mewakili kepentingan bisnis dan mengelola prioritas Product Backlog.",
    },
    {
        "kategori": "Materi 3",
        "pertanyaan": "Empat fase berurutan dalam metode Rapid Application Development (RAD) adalah...",
        "opsi_a": "Inception, Elicitation, Elaboration, Negotiation",
        "opsi_b": "Requirements Planning, User Design, Construction, Cutover",
        "opsi_c": "Planning, Risk Analysis, Engineering, Evaluation",
        "opsi_d": "Backlog, Sprint, Daily Meeting, Demo",
        "kunci_index": 1,
        "pembahasan": "Empat tahapan RAD meliputi Requirements Planning, User Design (JAD), Construction, dan Cutover.",
    },
    # Materi 4
    {
        "kategori": "Materi 4",
        "pertanyaan": "Tiga tokoh pelopor ('Three Amigos') yang menyatukan bahasa pemodelan OOD, OMT, dan OOSE menjadi UML pada tahun 1995 adalah...",
        "opsi_a": "Satzinger, Jackson, dan Burd",
        "opsi_b": "Booch, Rumbaugh, dan Jacobson",
        "opsi_c": "Pressman, Sommerville, dan Hoffer",
        "opsi_d": "Murdick, Ross, dan McLeod",
        "kunci_index": 1,
        "pembahasan": "Grady Booch, James Rumbaugh, dan Ivar Jacobson adalah pencetus standar Unified Modeling Language (UML).",
    },
    {
        "kategori": "Materi 4",
        "pertanyaan": "Relasi dalam Use Case Diagram yang bersifat OPSIONAL (hanya dijalankan pada kondisi tertentu) dan arah panahnya menunjuk ke use case dasar/utama adalah...",
        "opsi_a": "<<include>>",
        "opsi_b": "<<extend>>",
        "opsi_c": "Association",
        "opsi_d": "Boundary",
        "kunci_index": 1,
        "pembahasan": "Relasi <<extend>> digunakan untuk perluasan opsional dan panahnya mengarah ke use case dasar.",
    },
    {
        "kategori": "Materi 4",
        "pertanyaan": "Penekanan utama dalam pembuatan Use Case Diagram adalah menggambarkan...",
        "opsi_a": "Bagaimana algoritma kode program dieksekusi di memori",
        "opsi_b": "Struktur tabel dan relasi foreign key di database",
        "opsi_c": "Apa yang diperbuat/disediakan sistem (fungsionalitas) bagi aktor",
        "opsi_d": "Spesifikasi perangkat keras jaringan server",
        "kunci_index": 2,
        "pembahasan": "Use Case Diagram menggambarkan kebutuhan fungsional ('what the system does') dari perspektif pengguna (Actor).",
    },
    # Materi 5
    {
        "kategori": "Materi 5",
        "pertanyaan": "Urutan 4 langkah utama dalam tahapan Analisis Sistem yang benar adalah...",
        "opsi_a": "Plan - Code - Test - Deploy",
        "opsi_b": "Identify - Understand - Analyze - Report",
        "opsi_c": "Design - Implement - Convert - Maintain",
        "opsi_d": "Survey - Flowchart - Gantt Chart - Cutover",
        "kunci_index": 1,
        "pembahasan": "Empat tahap analisis sistem yaitu Identify (Identifikasi masalah), Understand (Memahami kerja sistem), Analyze (Menganalisis), dan Report (Melaporkan hasil).",
    },
    {
        "kategori": "Materi 5",
        "pertanyaan": "Pendekatan konversi sistem yang mengoperasikan sistem baru BERSAMAAN dengan sistem lama selama periode waktu tertentu agar aman jika sistem baru gagal disebut...",
        "opsi_a": "Konversi Langsung (Direct)",
        "opsi_b": "Konversi Paralel (Parallel)",
        "opsi_c": "Konversi Percontohan (Pilot)",
        "opsi_d": "Konversi Bertahap (Phased)",
        "kunci_index": 1,
        "pembahasan": "Konversi Paralel menjalankan sistem lama dan baru secara bersamaan untuk meminimalkan risiko kegagalan.",
    },
    {
        "kategori": "Materi 5",
        "pertanyaan": "Kesalahan program yang terjadi ketika sintaks kode sudah benar namun hasil perhitungan tidak sesuai yang diharapkan disebut...",
        "opsi_a": "Syntax Error",
        "opsi_b": "Language Error",
        "opsi_c": "Logical Error",
        "opsi_d": "Hardware Error",
        "kunci_index": 2,
        "pembahasan": "Logical Error terjadi akibat kesalahan logika/rumus meskipun program berhasil dikompilasi tanpa Syntax Error.",
    },
    # Materi 6
    {
        "kategori": "Materi 6",
        "pertanyaan": "Memperbaiki rumus perhitungan total belanja yang salah pada aplikasi kasir termasuk ke dalam jenis pemeliharaan...",
        "opsi_a": "Preventive Maintenance",
        "opsi_b": "Adaptive Maintenance",
        "opsi_c": "Corrective Maintenance",
        "opsi_d": "Perfective Maintenance",
        "kunci_index": 2,
        "pembahasan": "Corrective Maintenance berfokus pada perbaikan bug atau kesalahan logika yang ditemukan saat sistem berjalan.",
    },
    {
        "kategori": "Materi 6",
        "pertanyaan": "Indikator pengukuran efektivitas pemeliharaan yang menghitung rata-rata waktu antar kegagalan sistem disebut...",
        "opsi_a": "MTBF (Mean Time Between Failures)",
        "opsi_b": "SMLC (System Maintenance Life Cycle)",
        "opsi_c": "CMS (Change Management System)",
        "opsi_d": "JAD (Joint Application Development)",
        "kunci_index": 0,
        "pembahasan": "MTBF mengukur keandalan sistem berdasarkan rata-rata waktu operasional di antara dua kegagalan.",
    },
    {
        "kategori": "Materi 6",
        "pertanyaan": "Proses menganalisis suatu sistem yang sudah ada untuk mengidentifikasi elemen-elemennya dan menciptakan dokumentasi sistem yang sebelumnya tidak ada disebut...",
        "opsi_a": "Forward Engineering",
        "opsi_b": "Reverse Engineering",
        "opsi_c": "Direct Conversion",
        "opsi_d": "Unit Testing",
        "kunci_index": 1,
        "pembahasan": "Reverse Engineering mengekstrak rancangan dan dokumentasi dari kode atau sistem yang sudah berjalan.",
    },
    # Soal UAS (Evaluasi Akhir Komprehensif)
    {
        "kategori": "Soal UAS",
        "pertanyaan": "[UAS 1] Manakah pasangan fase SDLC dan deliverable (keluaran utama) yang TEPAT di bawah ini?",
        "opsi_a": "Planning -> menghasilkan System Proposal",
        "opsi_b": "Analysis -> menghasilkan Source Code Error-Free",
        "opsi_c": "Design -> menghasilkan Project Charter awal",
        "opsi_d": "Implementation -> menghasilkan Preliminary Scope",
        "kunci_index": 0,
        "pembahasan": "Fase Planning menghasilkan System Proposal yang memuat analisis kelayakan bisnis, teknis, dan organisasi.",
    },
    {
        "kategori": "Soal UAS",
        "pertanyaan": "[UAS 2] Pada Use Case Diagram EduAPS, setiap kali pengguna mengerjakan Tryout (Materi 1..6 maupun Soal UAS), sistem WAJIB menampilkan 'Hasil Ujian'. Relasi UML yang digunakan adalah...",
        "opsi_a": "<<extend>>",
        "opsi_b": "<<include>>",
        "opsi_c": "Generalization",
        "opsi_d": "System Boundary",
        "kunci_index": 1,
        "pembahasan": "Relasi <<include>> menunjukkan bahwa use case Hasil Ujian wajib dieksekusi sebagai bagian dari pengerjaan Tryout.",
    },
    {
        "kategori": "Soal UAS",
        "pertanyaan": "[UAS 3] Pada Sequence Diagram 'Taking a Tryout & Viewing Exam Results', komponen sistem yang bertugas menghitung skor (Calculate Score) dan menyimpan hasil ke Database adalah...",
        "opsi_a": "Interface",
        "opsi_b": "Tryout System",
        "opsi_c": "Grading System",
        "opsi_d": "File Storage",
        "kunci_index": 2,
        "pembahasan": "Sesuai Sequence Diagram, Tryout System meneruskan jawaban ke Grading System untuk menghitung skor dan menyimpan hasil ujian ke Database.",
    },
    {
        "kategori": "Soal UAS",
        "pertanyaan": "[UAS 4] Menyesuaikan format laporan sistem informasi akuntansi perusahaan karena adanya Undang-Undang Perpajakan baru dari pemerintah merupakan contoh...",
        "opsi_a": "Corrective Maintenance",
        "opsi_b": "Preventive Maintenance",
        "opsi_c": "Adaptive Maintenance",
        "opsi_d": "Reverse Engineering",
        "kunci_index": 2,
        "pembahasan": "Adaptive Maintenance dilakukan untuk menyesuaikan sistem terhadap perubahan regulasi atau lingkungan eksternal.",
    },
    {
        "kategori": "Soal UAS",
        "pertanyaan": "[UAS 5] Pendekatan konversi sistem yang menerapkan sistem baru di SATU cabang perusahaan terlebih dahulu sebagai percontohan sebelum diterapkan ke cabang lainnya disebut...",
        "opsi_a": "Konversi Langsung (Direct)",
        "opsi_b": "Konversi Paralel (Parallel)",
        "opsi_c": "Konversi Percontohan (Pilot)",
        "opsi_d": "Konversi Bertahap (Phased)",
        "kunci_index": 2,
        "pembahasan": "Konversi Pilot (Percontohan) menguji coba sistem baru pada satu unit/cabang organisasi terlebih dahulu.",
    },
    {
        "kategori": "Soal UAS",
        "pertanyaan": "[UAS 6] Pada Sequence Diagram 'UML Maker Application', proses pengeditan diagram dalam blok loop mendukung empat aksi utama berikut, KECUALI...",
        "opsi_a": "inputShape(type, label)",
        "opsi_b": "relocateShape(shapeId, newCoords)",
        "opsi_c": "deleteShape(shapeId)",
        "opsi_d": "compileJavaBytecode(className)",
        "kunci_index": 3,
        "pembahasan": "Empat aksi utama di dalam loop Editing Diagram adalah inputShape, relocateShape, deleteShape, dan connectShapes.",
    },
]


def seed_initial_data():
    db = SessionLocal()
    try:
        if db.query(Materi).count() == 0:
            for m in SEED_MATERI:
                db.add(Materi(**m))
            db.commit()

        if db.query(SoalTryout).count() == 0:
            for s in SEED_SOAL:
                db.add(SoalTryout(**s))
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


seed_initial_data()


# ==================== PYDANTIC SCHEMAS ====================
class MateriSummaryResponse(BaseModel):
    id: int
    kode: str
    minggu: str
    judul: str
    ringkasan: Optional[str] = None

    class Config:
        from_attributes = True


class MateriDetailResponse(MateriSummaryResponse):
    konten_html: str


class SoalTryoutResponse(BaseModel):
    id: int
    kategori: str
    pertanyaan: str
    opsi: List[str]
    kunci_index: int
    pembahasan: Optional[str] = None


class SubmitTryoutInput(BaseModel):
    nama_user: str = "Mahasiswa"
    kategori: str
    jawaban_user: Dict[int, int]  # {soal_id_atau_index: pilihan_index}


class HasilUjianResponse(BaseModel):
    id: int
    nama_user: str
    kategori_tryout: str
    jumlah_benar: int
    total_soal: int
    skor: int
    waktu_selesai: datetime

    class Config:
        from_attributes = True


class TanyaInput(BaseModel):
    nama_user: str
    isi_pertanyaan: str


class JawabInput(BaseModel):
    pertanyaan_id: int
    nama_user: str
    isi_jawaban: str


class JawabanResponse(BaseModel):
    id: int
    pertanyaan_id: int
    nama_user: str
    isi_jawaban: str
    waktu_dijawab: datetime

    class Config:
        from_attributes = True


class PertanyaanResponse(BaseModel):
    id: int
    nama_user: str
    isi_pertanyaan: str
    waktu_dibuat: datetime
    jawaban_list: List[JawabanResponse] = []

    class Config:
        from_attributes = True


class SaveUMLInput(BaseModel):
    judul_diagram: str
    tipe_diagram: str
    format_file: str = "svg"
    data_json: Optional[str] = None
    konten_svg: str


class FileUMLResponse(BaseModel):
    id: int
    judul_diagram: str
    tipe_diagram: str
    format_file: str
    waktu_disimpan: datetime

    class Config:
        from_attributes = True


# ==================== ENDPOINT HALAMAN UTAMA & STATUS ====================
@app.get("/")
def serve_frontend():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    return FileResponse(html_path)


@app.get("/api/status")
def cek_status():
    return {
        "status": "online",
        "database_engine": ACTIVE_DB_ENGINE,
        "modules": [
            "Ruang Belajar (System Control)",
            "Ruang Tryout & Grading System",
            "Forum Tanya Jawab (Forum System)",
            "Aplikasi Pembuat UML (File Storage)",
        ],
    }


# ==================== 1. ENDPOINTS RUANG BELAJAR ====================
# Sesuai Sequence Diagram: Mengakses Ruang Belajar
@app.get("/api/ruang-belajar", response_model=List[MateriSummaryResponse])
def get_materi_dan_ruang_belajar(db: Session = Depends(get_db)):
    """1.1 Request Data Ruang Belajar -> 1.2 Get Materi & Ruang Belajar()"""
    return db.query(Materi).order_by(Materi.id.asc()).all()


@app.get("/api/ruang-belajar/{materi_id}", response_model=MateriDetailResponse)
def get_detail_materi(materi_id: int, db: Session = Depends(get_db)):
    """2.1 Request Detail Materi() -> 2.2 Get Detail Materi(materiId)"""
    materi = db.query(Materi).filter(Materi.id == materi_id).first()
    if not materi:
        raise HTTPException(status_code=404, detail="Materi tidak ditemukan.")
    return materi


# ==================== 2. ENDPOINTS RUANG TRYOUT & GRADING SYSTEM ====================
# Sesuai Sequence Diagram: Taking a Tryout & Viewing Exam Results
@app.get("/api/tryout/questions/{kategori}", response_model=List[SoalTryoutResponse])
def request_tryout_questions(kategori: str, db: Session = Depends(get_db)):
    """2. Request Tryout Questions -> 3. Fetch Questions -> 4. Return Questions"""
    rows = (
        db.query(SoalTryout)
        .filter(SoalTryout.kategori == kategori)
        .order_by(SoalTryout.id.asc())
        .all()
    )
    if not rows:
        raise HTTPException(
            status_code=404, detail=f"Soal untuk kategori '{kategori}' belum tersedia."
        )
    return [
        SoalTryoutResponse(
            id=r.id,
            kategori=r.kategori,
            pertanyaan=r.pertanyaan,
            opsi=[r.opsi_a, r.opsi_b, r.opsi_c, r.opsi_d],
            kunci_index=r.kunci_index,
            pembahasan=r.pembahasan,
        )
        for r in rows
    ]


@app.post("/api/tryout/submit", response_model=HasilUjianResponse)
def submit_answers_and_start_grading(
    payload: SubmitTryoutInput, db: Session = Depends(get_db)
):
    """
    8. Submit Answers & Start Grading -> 9. Answers -> 10. Calculate Score ->
    11. Save Test Results -> 12. Confirmation -> 13/14. Exam Results & Score
    """
    soal_list = (
        db.query(SoalTryout)
        .filter(SoalTryout.kategori == payload.kategori)
        .order_by(SoalTryout.id.asc())
        .all()
    )
    if not soal_list:
        raise HTTPException(status_code=404, detail="Kategori tryout tidak ditemukan.")

    benar = 0
    for idx, soal in enumerate(soal_list):
        pilihan = payload.jawaban_user.get(soal.id, payload.jawaban_user.get(idx))
        if pilihan is not None and int(pilihan) == soal.kunci_index:
            benar += 1

    total = len(soal_list)
    skor = round((benar / total) * 100) if total > 0 else 0

    hasil_baru = HasilUjian(
        nama_user=(payload.nama_user or "Mahasiswa").strip() or "Mahasiswa",
        kategori_tryout=payload.kategori,
        jumlah_benar=benar,
        total_soal=total,
        skor=skor,
    )
    db.add(hasil_baru)
    db.commit()
    db.refresh(hasil_baru)
    return hasil_baru


@app.get("/api/tryout/hasil", response_model=List[HasilUjianResponse])
def ambil_riwayat_hasil_ujian(db: Session = Depends(get_db)):
    """Mengambil daftar riwayat Hasil Ujian dari Database."""
    return (
        db.query(HasilUjian)
        .order_by(HasilUjian.waktu_selesai.desc())
        .limit(20)
        .all()
    )


# ==================== 3. ENDPOINTS FORUM TANYA JAWAB ====================
# Sesuai Sequence Diagram: Using a Q&A Forum (Forum Tanya Jawab)
@app.get("/api/forum", response_model=List[PertanyaanResponse])
def ambil_semua_forum(db: Session = Depends(get_db)):
    """getDiscussions() -> fetchQuestionsAndAnswers() -> discussionData"""
    pertanyaan = (
        db.query(Pertanyaan)
        .options(joinedload(Pertanyaan.jawaban_list))
        .order_by(Pertanyaan.waktu_dibuat.desc())
        .all()
    )
    return pertanyaan


@app.post("/api/forum/tanya", response_model=PertanyaanResponse)
def tambah_pertanyaan(data: TanyaInput, db: Session = Depends(get_db)):
    """submitQuestion(text) -> saveNewQuestion(text) -> success / questionId"""
    if not data.nama_user.strip() or not data.isi_pertanyaan.strip():
        raise HTTPException(
            status_code=400, detail="Nama dan isi pertanyaan tidak boleh kosong."
        )

    pertanyaan_baru = Pertanyaan(
        nama_user=data.nama_user.strip(),
        isi_pertanyaan=data.isi_pertanyaan.strip(),
    )
    db.add(pertanyaan_baru)
    db.commit()
    db.refresh(pertanyaan_baru)
    return pertanyaan_baru


@app.post("/api/forum/jawab", response_model=JawabanResponse)
def tambah_jawaban(data: JawabInput, db: Session = Depends(get_db)):
    """submitAnswer(questionId, text) -> saveNewAnswer(questionId, text) -> success / answerId"""
    cek_pertanyaan = (
        db.query(Pertanyaan).filter(Pertanyaan.id == data.pertanyaan_id).first()
    )
    if not cek_pertanyaan:
        raise HTTPException(status_code=404, detail="Pertanyaan tidak ditemukan.")

    if not data.nama_user.strip() or not data.isi_jawaban.strip():
        raise HTTPException(
            status_code=400, detail="Nama dan isi jawaban tidak boleh kosong."
        )

    jawaban_baru = Jawaban(
        pertanyaan_id=data.pertanyaan_id,
        nama_user=data.nama_user.strip(),
        isi_jawaban=data.isi_jawaban.strip(),
    )
    db.add(jawaban_baru)
    db.commit()
    db.refresh(jawaban_baru)
    return jawaban_baru


# ==================== 4. ENDPOINTS APLIKASI PEMBUAT UML ====================
# Sesuai Sequence Diagram: UML Maker Application (File Storage)
@app.post("/api/uml/save", response_model=FileUMLResponse)
def simpan_file_uml(data: SaveUMLInput, db: Session = Depends(get_db)):
    """generateFile(data, format) -> saveFile(file) -> fileSaved -> downloadReady"""
    file_baru = FileUML(
        judul_diagram=data.judul_diagram.strip() or "Diagram UML EduAPS",
        tipe_diagram=data.tipe_diagram,
        format_file=data.format_file,
        data_json=data.data_json,
        konten_svg=data.konten_svg,
    )
    db.add(file_baru)
    db.commit()
    db.refresh(file_baru)
    return file_baru


@app.get("/api/uml/files", response_model=List[FileUMLResponse])
def daftar_file_uml(db: Session = Depends(get_db)):
    return db.query(FileUML).order_by(FileUML.waktu_disimpan.desc()).limit(15).all()
