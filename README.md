uvicorn main:app --reload

        # High-quality embeddings for skills and tasks
        # Specialized embeddings for skills (optimized for technical terms and expertise)
        # self.skills_embeddings = HuggingFaceEmbeddings(
        #     model_name="BAAI/bge-large-en",
        #     model_kwargs={"device": "cpu"},
        #     encode_kwargs={
        #         "normalize_embeddings": True,
        #         "instruction": "Represent this professional skill for matching with job requirements:",
        #     },
        # )

        # # Specialized embeddings for tasks (optimized for project requirements)
        # self.tasks_embeddings = HuggingFaceEmbeddings(
        #     model_name="BAAI/bge-large-en",
        #     model_kwargs={"device": "cpu"},
        #     encode_kwargs={
        #         "normalize_embeddings": True,
        #         "instruction": "Represent this project task for matching with professional skills:",
        #     },
        # )

        # HuggingFace API embeddings
        # self.skills_embeddings = HuggingFaceHubEmbeddings(
        #     repo_id="sentence-transformers/all-MiniLM-L6-v2",
        #     task="feature-extraction"
        # )

        # self.tasks_embeddings = HuggingFaceHubEmbeddings(
        #     repo_id="sentence-transformers/all-MiniLM-L6-v2",
        #     task="feature-extraction"
        # )
