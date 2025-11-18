from aiogram import Router
from aiogram.filters.command import Command
from aiogram import types

from aiogram.fsm.state import StatesGroup
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext

from app.utils.watcher import wallet_watcher
from app.utils.validator import is_valid_wallet_address

from app.constants.content import WATCHLIST_MENU, INVALID_WALLET_ADDRESS, WALLET_ADDED, AVAILABLE_COMMANDS, FILTER_SETS_MENU, MY_STATS_MENU, GUIDE_MENU

from app.db.db import get_data, add_data
from app.keyboards.inline import get_inline_keyboard
from app.keyboards.reply import get_reply_keyboard

import asyncio
import random

# For logging
import logging

from app.services.user_service import (
    add_wallet,
    wallet_exists,
    get_wallets,
    get_user
)

watch_router = Router()
wallet_tasks = {}

menus = {}

class WatchStates(StatesGroup):
    waiting_for_address = State()
    waiting_for_name = State()
    waiting_for_rename = State()

@watch_router.message(lambda msg: msg.text == WATCHLIST_MENU)
async def handle_watchmenu(msg: types.Message):
    logging.info(f"User {msg.from_user.id} opened watchlist menu.")

    user_id = msg.chat.id
    user_data = get_data('users', user_id)

    keyboard_list = [[("➕ Add Wallet", 'add_wallet'), ('✏️ Rename', 'rename_wallet')], [('🗑 Remove', 'remove_wallet'), ('🔙 Back','back_menu')]]
    inline_keyboard = get_inline_keyboard(keyboard_list)

    circles = ['🔵', '🟢', '🟡', '🟠', '🔴', '🟣']

    if not user_data or 'wallets' not in user_data:
        keyboard_list = [[("➕ Add Wallet", 'add_wallet')], [('🔙 Back','back_menu')]]
        inline_keyboard = get_inline_keyboard(keyboard_list)

        await msg.answer("You have no wallets in your list.",
                         reply_markup=inline_keyboard)
        return

    items = user_data['wallets']
    if not items:
        keyboard_list = [[("➕ Add Wallet", 'add_wallet')], [('🔙 Back','back_menu')]]
        inline_keyboard = get_inline_keyboard(keyboard_list)

        await msg.answer("You have no wallets in your list.",
                         reply_markup=inline_keyboard)
        return

    response = "<b>Your Watchlist:</b>\n\n"

    if not items:
        await msg.answer(text="You have no wallets in your list.")
        return

    for index, item in enumerate(items, start=1):

        circle = random.choice(circles)

        name = item.get("name")
        address = item.get("address")

        if name:
            line = f"{index}. {circle} {name} ({address[:6]}...{address[-4:]})"
        else:
            line = f"{index}. {circle} {address[:6]}...{address[-4:]} (unnamed)"

        response += line + "\n"

    watchlist_menu = await msg.answer(response, reply_markup=inline_keyboard)
    menus[user_id] = watchlist_menu

@watch_router.callback_query(lambda c: c.data)
async def handle_watch(callback: types.CallbackQuery, state: FSMContext):

    logging.info(f"User {callback.from_user.id} triggered watchlist callback: {callback.data}")
    
    user_id = callback.message.chat.id

    if callback.data == 'add_wallet':
        keyboard = get_inline_keyboard([[("🔙 Back", 'back_menu')]])
        await callback.message.answer("🔍 Send the wallet address you want to track (0x...)", reply_markup=keyboard)
        await state.set_state(WatchStates.waiting_for_address)
    elif callback.data == 'name_wallet':
        keyboard = get_inline_keyboard([[("🔙 Back", 'back_menu')]])
        await callback.message.answer("✏️ Enter wallet name:\n\nExamples:\n- TrumpWhale\n- SharpMoney 1\n- Insider Alpha", reply_markup=keyboard)
        await state.set_state(WatchStates.waiting_for_name)

    elif callback.data == "remove_wallet":
        wallets = get_wallets(user_id)
        if not wallets:
            await callback.message.answer("⚠️ You have no wallets to remove.")
            return

        wallet_keyboard = []

        for item in wallets:
            name = item.get("name")
            address = item.get("address")
            display_name = name if name else f"{address[:6]}...{address[-4:]}"
            wallet_keyboard.append([(display_name, f'remove_{address}')])
        
        wallet_keyboard.append([("🔙 Back", 'back_menu')])
        
        inline_keyboard = get_inline_keyboard(wallet_keyboard)
        await callback.message.answer(text="Select wallet to remove: ", reply_markup=inline_keyboard)
    

    elif callback.data == "rename_wallet":
        wallets = get_wallets(user_id)
        if not wallets:
            await callback.message.answer("⚠️ You have no wallets to rename.")
            return

        wallet_keyboard = []

        for item in wallets:
            name = item.get("name")
            address = item.get("address")
            display_name = name if name else f"{address[:6]}...{address[-4:]}"
            wallet_keyboard.append([(display_name, f'rename_{address}')])
        
        wallet_keyboard.append([("🔙 Back", 'back_menu')])
        
        inline_keyboard = get_inline_keyboard(wallet_keyboard)
        await callback.message.answer(text="Select wallet to rename: ", reply_markup=inline_keyboard)
    
    elif callback.data.startswith('rename_'):
        wallet_address = callback.data.split('_')[1]
        keyboard = get_inline_keyboard([[("🔙 Back", 'back_menu')]])
        await state.set_data({"wallet_address": wallet_address})
        await callback.message.answer("✏️ Enter new wallet name:", reply_markup=keyboard)
        await state.set_state(WatchStates.waiting_for_rename)

    elif callback.data.startswith('remove_'):
        wallet_address = callback.data.split('_')[1]
        
        wallets = get_wallets(user_id)
        for w in wallets:
            if w["address"].lower() == wallet_address.lower():
                confirmational_keyboard = get_inline_keyboard([[("✔️ Yes, remove", f'confirm_remove_{wallet_address}')], [("❌ Cancel", 'back_menu')]])
                
                if w.get("name"):
                    await callback.message.answer(f'Are you sure you want to remove wallet "{w["name"]}"?', reply_markup=confirmational_keyboard)
                else:
                    await callback.message.answer(f"Are you sure you want to remove wallet {wallet_address[:6]}...{wallet_address[-4:]}?", reply_markup=confirmational_keyboard)
                
                break
    
    elif callback.data.startswith('confirm_remove_'):
        wallet_address = callback.data.split('_')[2]
        user = get_user(user_id)
        
        wallets = user.get("wallets", [])
        wallets = [w for w in wallets if w["address"].lower() != wallet_address.lower()]
        
        add_data("users", user_id, {"wallets": wallets})

        task_id = f"{user_id}:{wallet_address}"
        if task_id in wallet_tasks:
            wallet_tasks[task_id].cancel()
            del wallet_tasks[task_id]

        await callback.message.answer("🗑 Wallet removed.")

    
    elif callback.data == 'skip_naming':
        storage = await state.get_data()
        wallet_address = storage.get('wallet_address')

        await callback.message.answer(f"✔️ Wallet saved.\nDefault name: {wallet_address[:6]}...{wallet_address[-4:]}")
        add_wallet(user_id=user_id,wallet_address=wallet_address, wallet_name=None)

        task_id = f"{user_id}:{wallet_address}"

        if task_id not in wallet_tasks:
            wallet_tasks[task_id] = asyncio.create_task(wallet_watcher(user_id, wallet_address, callback.bot))

        await state.clear()

    elif callback.data == 'back_menu':
        buttons = get_reply_keyboard([[WATCHLIST_MENU, FILTER_SETS_MENU], 
                                    [MY_STATS_MENU, GUIDE_MENU]])
        
        try:
            await callback.message.delete()
            await callback.message.answer(text="🏡 Back in home menu.",
                                        reply_markup=buttons)
        except:
            pass

        await state.clear()
    
@watch_router.message(WatchStates.waiting_for_name)
async def process_wallet_name(msg: types.Message, state: FSMContext):
    user_id = msg.chat.id
    wallet_name = msg.text.strip()
    storage = await state.get_data()
    wallet_address = storage.get("wallet_address")

    if not wallet_address:
        await msg.answer(INVALID_WALLET_ADDRESS)
        await state.clear()
        return

    await msg.answer(f"✔️ Saved!\nWallet named as: {wallet_name}")

    add_wallet(user_id=user_id, 
               wallet_address=wallet_address, 
               wallet_name=wallet_name)
    
    # TODO: need to firstly:
    # - save tasks to the DB
    # - launch them after bot restart
    task_id = f"{user_id}:{wallet_address}"

    if task_id not in wallet_tasks:
        wallet_tasks[task_id] = asyncio.create_task(wallet_watcher(user_id, wallet_address, msg.bot))

    await state.clear()
    

@watch_router.message(WatchStates.waiting_for_rename)
async def process_wallet_rename(msg: types.Message, state: FSMContext):
    user_id = msg.chat.id
    new_name = msg.text.strip()

    user = get_user(user_id)
    
    wallets = user.get("wallets", [])
    wallet_address = (await state.get_data()).get("wallet_address")

    for w in wallets:
        if w["address"].lower() == wallet_address.lower():
            w["name"] = new_name
            break

    add_data("users", user_id, {"wallets": wallets})

    await msg.answer(f"✔️ Name updated!\nNew name: {new_name}")    


@watch_router.message(WatchStates.waiting_for_address)
async def process_wallet_address(msg: types.Message, state: FSMContext):
    address = msg.text.strip()

    inline_keyboard = get_inline_keyboard([[("✏️ Yes, name wallet", 'name_wallet')], [('⏭️ Skip', 'skip_naming')]])
    
    if not is_valid_wallet_address(address):
        await msg.answer(text=INVALID_WALLET_ADDRESS)
        return

    if wallet_exists(msg.from_user.id, address):
        back_keyboard = get_inline_keyboard([[("🔙 Back", 'back_menu')]])
        await msg.answer(text="⚠️ This wallet is already in your watchlist.", reply_markup=back_keyboard)
        await state.clear()
        return
    
    await state.set_data({"wallet_address": address})

    await msg.answer(text=WALLET_ADDED,
                     reply_markup=inline_keyboard)
