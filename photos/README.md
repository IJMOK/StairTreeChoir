Tread measurement photos (CLAUDE.md section 9).

Phone photos carry the GPS position of where they were taken. Strip it before committing (tests/test_photos.py fails otherwise), losslessly:

    .venv/Scripts/python -c "import piexif,sys; [piexif.insert(piexif.dump({**piexif.load(f), 'GPS': {}}), f) for f in sys.argv[1:]]" photos/NEW.jpg
