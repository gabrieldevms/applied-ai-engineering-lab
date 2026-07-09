from ai_api.rag.schemas import DocumentChunk, DocumentChunkingResponse


class TextChunker:
    def chunk(
        self,
        document_text: str,
        source: str = "manual",
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ) -> DocumentChunkingResponse:
        cleaned_text = document_text.strip()
        cleaned_source = source.strip()

        if not cleaned_text:
            raise ValueError("document_text cannot be blank")

        if not cleaned_source:
            raise ValueError("source cannot be blank")

        if chunk_size < 1:
            raise ValueError("chunk_size must be greater than zero")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        chunks = self._build_chunks(
            text=cleaned_text,
            source=cleaned_source,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        return DocumentChunkingResponse(
            source=cleaned_source,
            total_chunks=len(chunks),
            chunks=chunks,
        )

    def _build_chunks(
        self,
        text: str,
        source: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        text_length = len(text)
        start_index = 0

        while start_index < text_length:
            end_index = min(start_index + chunk_size, text_length)

            if end_index < text_length:
                split_index = text.rfind(" ", start_index, end_index)

                if split_index > start_index + int(chunk_size * 0.5):
                    end_index = split_index

            content = text[start_index:end_index].strip()

            if content:
                chunk_index = len(chunks)

                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{source}-{chunk_index}",
                        source=source,
                        content=content,
                        start_index=start_index,
                        end_index=end_index,
                        chunk_index=chunk_index,
                        metadata={
                            "chunk_size": chunk_size,
                            "chunk_overlap": chunk_overlap,
                        },
                    )
                )

            if end_index >= text_length:
                break

            next_start_index = max(end_index - chunk_overlap, start_index + 1)
            start_index = self._move_start_to_word_boundary(
                text=text,
                start_index=next_start_index,
            )

        return chunks

    def _move_start_to_word_boundary(
        self,
        text: str,
        start_index: int,
    ) -> int:
        if start_index <= 0:
            return 0

        text_length = len(text)

        if start_index >= text_length:
            return text_length

        while start_index < text_length and text[start_index].isspace():
            start_index += 1

        if start_index >= text_length:
            return text_length

        if text[start_index - 1].isspace():
            return start_index

        next_space_index = text.find(" ", start_index)

        if next_space_index == -1:
            return start_index

        return next_space_index + 1
