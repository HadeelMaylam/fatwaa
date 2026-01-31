"""
Supabase service for database operations.
Handles fetching fatwas, shaykhs, and series data.
"""

from supabase import create_client, Client
from typing import List, Optional, Dict, Any
from uuid import UUID
from loguru import logger

from app.config import settings
from app.models import FatwaDetail


class SupabaseService:
    """Service for interacting with Supabase database."""

    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
        logger.info("Supabase client initialized")

    async def test_connection(self) -> bool:
        """Test Supabase connection."""
        try:
            # Simple query to test connection
            result = self.client.table("shaykhs").select("id").limit(1).execute()
            logger.info("Supabase connection successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection failed: {e}")
            return False

    def get_all_fatwas(self) -> List[FatwaDetail]:
        """
        Fetch all fatwas with shaykh and series names.
        Used for indexing into Qdrant.
        Fetches in batches to handle large datasets.

        Returns:
            List of FatwaDetail objects
        """
        try:
            logger.info("Fetching all fatwas from database...")

            all_fatwas = []
            batch_size = 1000
            offset = 0

            while True:
                # Query with joins to get shaykh and series names
                result = self.client.table("fatwa_details") \
                    .select("""
                        id,
                        category,
                        question,
                        answer,
                        link,
                        shaykh_id,
                        series_id,
                        shaykhs(name),
                        series(name)
                    """) \
                    .range(offset, offset + batch_size - 1) \
                    .execute()

                if not result.data:
                    break

                # Process batch
                for row in result.data:
                    # Skip fatwas with missing critical data
                    if not row.get("question") or not row.get("answer"):
                        logger.debug(f"Skipping fatwa {row.get('id')} - missing question or answer")
                        continue

                    try:
                        fatwa = FatwaDetail(
                            id=row["id"],
                            category=row.get("category", ""),
                            question=row["question"],
                            answer=row["answer"],
                            link=row.get("link", ""),
                            shaykh_id=row["shaykh_id"],
                            series_id=row["series_id"],
                            shaykh_name=row["shaykhs"]["name"] if row.get("shaykhs") else None,
                            series_name=row["series"]["name"] if row.get("series") else None
                        )
                        all_fatwas.append(fatwa)
                    except Exception as e:
                        logger.warning(f"Error processing fatwa {row.get('id')}: {e}")
                        continue

                logger.info(f"Fetched batch: {len(all_fatwas)} fatwas so far...")

                # If we got less than batch_size, we're done
                if len(result.data) < batch_size:
                    break

                offset += batch_size

            logger.info(f"Fetched {len(all_fatwas)} fatwas from database in total")
            return all_fatwas

        except Exception as e:
            logger.error(f"Error fetching fatwas: {e}")
            raise

    def get_fatwa_by_id(self, fatwa_id: UUID) -> Optional[FatwaDetail]:
        """
        Get a specific fatwa by ID with shaykh and series info.

        Args:
            fatwa_id: UUID of the fatwa

        Returns:
            FatwaDetail object or None
        """
        try:
            result = self.client.table("fatwa_details") \
                .select("""
                    id,
                    category,
                    question,
                    answer,
                    link,
                    shaykh_id,
                    series_id,
                    shaykhs(name),
                    series(name)
                """) \
                .eq("id", str(fatwa_id)) \
                .execute()

            if not result.data:
                return None

            row = result.data[0]
            return FatwaDetail(
                id=row["id"],
                category=row["category"],
                question=row["question"],
                answer=row["answer"],
                link=row["link"],
                shaykh_id=row["shaykh_id"],
                series_id=row["series_id"],
                shaykh_name=row["shaykhs"]["name"] if row.get("shaykhs") else None,
                series_name=row["series"]["name"] if row.get("series") else None
            )

        except Exception as e:
            logger.error(f"Error fetching fatwa {fatwa_id}: {e}")
            return None

    def get_fatwas_by_ids(self, fatwa_ids: List[str]) -> List[FatwaDetail]:
        """
        Get multiple fatwas by IDs (used after Qdrant search).

        Args:
            fatwa_ids: List of fatwa UUID strings

        Returns:
            List of FatwaDetail objects
        """
        try:
            result = self.client.table("fatwa_details") \
                .select("""
                    id,
                    category,
                    question,
                    answer,
                    link,
                    shaykh_id,
                    series_id,
                    shaykhs(name),
                    series(name)
                """) \
                .in_("id", fatwa_ids) \
                .execute()

            # Create a mapping for quick lookup
            fatwas_map = {}
            for row in result.data:
                fatwa = FatwaDetail(
                    id=row["id"],
                    category=row["category"],
                    question=row["question"],
                    answer=row["answer"],
                    link=row["link"],
                    shaykh_id=row["shaykh_id"],
                    series_id=row["series_id"],
                    shaykh_name=row["shaykhs"]["name"] if row.get("shaykhs") else None,
                    series_name=row["series"]["name"] if row.get("series") else None
                )
                fatwas_map[str(row["id"])] = fatwa

            # Return in same order as input IDs
            return [fatwas_map[fid] for fid in fatwa_ids if fid in fatwas_map]

        except Exception as e:
            logger.error(f"Error fetching fatwas by IDs: {e}")
            return []


# Global instance
supabase_service = SupabaseService()
