from app.core.iam.policy_store import policy_store, Policy
from app.core.rbac import Permission
from app.models.user import UserRole


# =========================================================
# IAM POLICY SEEDER (BOOTSTRAP SYSTEM POLICIES)
# =========================================================
class IAMPolicySeeder:
    """
    Seeds default AWS-style IAM policies into the system.

    Run once at application startup.
    """

    @staticmethod
    def seed():
        """
        Registers all default system policies.
        """

        # =====================================================
        # ADMIN FULL ACCESS POLICY
        # =====================================================
        policy_store.register(
            Policy(
                name="AdminFullAccess",
                description="Full system access for administrators",
                roles={UserRole.ADMIN},
                actions={
                    Permission.USER_READ,
                    Permission.USER_WRITE,
                    Permission.USER_DELETE,
                    Permission.USER_ROLE_UPDATE,

                    Permission.ADMIN_DASHBOARD,
                    Permission.ADMIN_READ,

                    Permission.ASSESSMENT_READ,
                    Permission.ASSESSMENT_WRITE,
                    Permission.ASSESSMENT_DELETE,

                    Permission.PREDICTION_READ,
                    Permission.PREDICTION_WRITE,
                    Permission.PREDICTION_DELETE,

                    Permission.DISEASE_READ,
                    Permission.DISEASE_WRITE,
                    Permission.DISEASE_DELETE,
                },
            )
        )

        # =====================================================
        # CLINICIAN SCOPED ACCESS POLICY
        # =====================================================
        policy_store.register(
            Policy(
                name="ClinicianReadWritePolicy",
                description="Clinician access to medical workflows",
                roles={UserRole.CLINICIAN},
                actions={
                    Permission.USER_READ,

                    Permission.ASSESSMENT_READ,
                    Permission.ASSESSMENT_WRITE,

                    Permission.PREDICTION_READ,
                    Permission.PREDICTION_WRITE,

                    Permission.DISEASE_READ,
                },
            )
        )

        # =====================================================
        # USER BASIC ACCESS POLICY
        # =====================================================
        policy_store.register(
            Policy(
                name="UserReadOnlyPolicy",
                description="Standard user limited access",
                roles={UserRole.USER},
                actions={
                    Permission.ASSESSMENT_READ,
                    Permission.PREDICTION_READ,
                    Permission.DISEASE_READ,
                },
            )
        )

        # =====================================================
        # SYSTEM SAFETY POLICY (EXAMPLE DENY RULE)
        # =====================================================
        policy_store.register(
            Policy(
                name="DenySystemDeleteProtection",
                description="Prevents accidental system-wide deletes",
                roles={UserRole.USER, UserRole.CLINICIAN},
                actions={
                    Permission.USER_DELETE,
                    Permission.USER_ROLE_UPDATE,
                },
            )
        )


# =========================================================
# AUTO-SEED FUNCTION (CALLED ON STARTUP)
# =========================================================
def seed_iam_policies():
    IAMPolicySeeder.seed()