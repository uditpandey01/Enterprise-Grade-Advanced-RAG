from typing import List
import logfire

def chunk_text(text: str, chunk_size: int = 1500) -> List[str]:
    with logfire.span("✂️ Text Chunking", text_length=len(text)):
        if not text.strip(): 
            return []
            
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""
        
        for p in paragraphs:
            if len(current_chunk) + len(p) < chunk_size:
                current_chunk += p + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = p + "\n\n"
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
            
        valid_chunks = [c for c in chunks if c.strip()]
        logfire.info(f"✅ Generated {len(valid_chunks)} chunks")
        return valid_chunks
    
# from typing import List

# import logfire
# from langchain_text_splitters import RecursiveCharacterTextSplitter


# def chunk_text(text: str, chunk_size: int = 1500) -> List[str]:
#     with logfire.span(" Text Chunking", text_length=len(text)):
#         if not text.strip():
#             return []

#         splitter = RecursiveCharacterTextSplitter(
#             chunk_size=chunk_size,
#             chunk_overlap=200,
#             separators=["\n\n", "\n", ".", " ", ""]
#         )

#         chunks = splitter.split_text(text)

#         logfire.info(f"✅ Generated {len(chunks)} chunks")

#         return chunks












"""
    Simple semantic-ish chunker that splits by paragraphs.
    Ensures chunks do not exceed the specified size.
"""
