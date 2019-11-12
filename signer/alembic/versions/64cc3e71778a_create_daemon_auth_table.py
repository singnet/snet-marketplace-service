"""create daemon auth table

Revision ID: 64cc3e71778a
Revises: 
Create Date: 2019-11-12 18:52:29.229539

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '64cc3e71778a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    # conn.execute("""CREATE TABLE `demon_auth_keys` (`org_id` varchar(225) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
    #                                                 `service_id` varchar(225) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
    #                                                 `group_id` varchar(225) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
    #                                                 `public_key` varchar(225) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
    #                                                 `id` int(11) NOT NULL AUTO_INCREMENT,
    #                                                 PRIMARY KEY (`id`)
    #             )""")


def downgrade():
    conn = op.get_bind()
    # conn.execute("""
    #         drop table demon_auth_keys;
    #         """)
