from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def suggest_icd_codes(diagnosis_text: str, session: AsyncSession, limit: int = 5):
    """
    Given a diagnosis text, searches the SQLite FTS5 table for the best matching ICD-10 codes.
    Returns a list of dictionaries with code, description, and confidence.
    """
    # Clean the diagnosis text for FTS (remove quotes, handle special chars)
    clean_text = "".join(c if c.isalnum() or c.isspace() else " " for c in diagnosis_text)
    words = clean_text.split()
    
    if not words:
        return []
        
    # We will do a simple prefix match on all words: "word1* word2*"
    query_str = " ".join([f"{w}*" for w in words if len(w) > 2])
    if not query_str:
         query_str = " ".join([f"{w}*" for w in words])
         
    # FTS5 query: order by rank (BM25 score)
    # The rank in FTS5 is a negative number, lower is better.
    stmt = text("""
        SELECT icd_codes.code, icd_codes.description, icd_search_fts.rank
        FROM icd_search_fts
        JOIN icd_codes ON icd_search_fts.rowid = icd_codes.rowid
        WHERE icd_search_fts MATCH :query
        ORDER BY icd_search_fts.rank
        LIMIT :limit
    """)
    
    result = await session.execute(stmt, {"query": query_str, "limit": limit})
    rows = result.fetchall()
    
    suggestions = []
    for r in rows:
        code, description, rank = r
        # FTS rank is a negative float. We will normalize it loosely to a 0-1 confidence.
        # This is a very rough normalization: -10 is very good, -1 is poor.
        base_confidence = min(0.95, max(0.1, abs(rank) / 10.0))
        
        suggestions.append({
            "code": code,
            "description": description,
            "confidence": round(base_confidence, 2)
        })
        
    # If no results from FTS matching all terms, we might try OR matching.
    if not suggestions:
        query_str_or = " OR ".join([f"{w}*" for w in words])
        stmt_or = text("""
            SELECT icd_codes.code, icd_codes.description, icd_search_fts.rank
            FROM icd_search_fts
            JOIN icd_codes ON icd_search_fts.rowid = icd_codes.rowid
            WHERE icd_search_fts MATCH :query
            ORDER BY icd_search_fts.rank
            LIMIT :limit
        """)
        try:
            result = await session.execute(stmt_or, {"query": query_str_or, "limit": limit})
            rows = result.fetchall()
            for r in rows:
                code, description, rank = r
                base_confidence = min(0.95, max(0.1, abs(rank) / 15.0))
                suggestions.append({
                    "code": code,
                    "description": description,
                    "confidence": round(base_confidence, 2)
                })
        except Exception:
            pass

    return suggestions
