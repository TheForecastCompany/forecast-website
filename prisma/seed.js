import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

async function main() {
  const user = await prisma.user.create({
    data: {
      username: 'testuser',
      password: 'password123',
    },
  });

  console.log('Seeded user:', user); // 👈 confirm data inserted
}

main()
  .catch(e => {
    console.error('Seed error:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });