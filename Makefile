.PHONY: pipeline app docs clean

pipeline:
	python pipeline.py

app:
	streamlit run streamlit_app.py

docs:
	python -m compileall streamlit_app.py pipeline.py

clean:
	rm -f cleaned_records.csv engagement_scores.csv student_clusters.csv cluster_profiles.csv
