const { PrismaClient } = require('@prisma/client')
const bcrypt = require('bcryptjs')
const readline = require('readline')

const prisma = new PrismaClient()

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
})

function question(prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, resolve)
  })
}

async function main() {
  try {
    console.log('Create Admin User\n')

    const email = await question('Email: ')
    const password = await question('Password: ')
    const name = await question('Name (optional): ')

    const hashedPassword = await bcrypt.hash(password, 10)

    const user = await prisma.user.create({
      data: {
        email,
        password: hashedPassword,
        name: name || null,
      },
    })

    console.log(`\n✅ Admin user created successfully!`)
    console.log(`Email: ${user.email}`)
  } catch (error) {
    if (error.code === 'P2002') {
      console.error('❌ User with this email already exists')
    } else {
      console.error('Error:', error.message)
    }
  } finally {
    rl.close()
    await prisma.$disconnect()
  }
}

main()

