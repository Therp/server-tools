# © 2018 Pieter Paulussen <pieter_paulussen@me.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging


def migrate(cr, version):
    if not version:
        return
    logger = logging.getLogger(__name__)
    logger.info(
        "Creating columns: auditlog_log_line (method. user_id) "
    )
    cr.execute(
        """
    ALTER TABLE auditlog_log_line
    ADD COLUMN IF NOT EXISTS method VARCHAR,
    ADD COLUMN IF NOT EXISTS user_id INTEGER,
    ADD COLUMN IF NOT EXISTS model_id INTEGER,
    ADD COLUMN IF NOT EXISTS res_id INTEGER;

    """
    )
    cr.execute(
       """
       ALTER TABLE auditlog_log_line DROP CONSTRAINT IF EXISTS  auditlog_log_line_user_id_fkey;
       ALTER TABLE auditlog_log_line  ADD constraint  
       auditlog_log_line_user_id_fkey 
       FOREIGN KEY (user_id)   REFERENCES res_users(id) ON DELETE SET NULL;
       ALTER TABLE auditlog_log_line DROP CONSTRAINT IF EXISTS  auditlog_log_line_model_id_fkey;
       ALTER TABLE auditlog_log_line  ADD constraint  
       auditlog_log_line_model_id_fkey 
       FOREIGN KEY (model_id)   REFERENCES ir_model(id) ON DELETE SET NULL;
       """
    )
    logger.info(
        "Creating indexes on auditlog_log_line column 'method'"
    )
    cr.execute(
        """
        CREATE INDEX IF NOT EXISTS
        auditlog_log_line_method_index ON auditlog_log_line (method);
        CREATE INDEX IF NOT EXISTS
        auditlog_log_line_user_id_index ON auditlog_log_line (user_id);
        CREATE INDEX IF NOT EXISTS
        auditlog_log_line_model_id_index ON auditlog_log_line (model_id);
        CREATE INDEX IF NOT EXISTS
        auditlog_log_line_res_id_index ON auditlog_log_line (res_id);
    """
    )
    logger.info(
        "Preemtive fill of auditlog_log_line columns: 'method', user_id, res_id, model_id"
    )
    cr.execute(
        """
    UPDATE auditlog_log_line aline
    SET method = al.method, user_id = al.user_id , model_id = al.model_id, res_id = al.res_id
    FROM auditlog_log al
    WHERE al.id = aline.log_id; 
    """
    )
    logger.info("Successfully updated auditlog tables")
