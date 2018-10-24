from flask import Flask, jsonify,request
from flask_restplus import reqparse

app = Flask(__name__)
process_dic={'order_placed':'being_prepared','being_prepared':'released','paid':'released'}
cost_dic = {'a':10,'b':12,'c':13,'d':14}
order_status_list = ['order_placed','being_prepared','paid','released']
payment_status_list = ['unpaid','paid']
orders_database = [
{
        'id': 0,
        'type of coffee': 'Coffee name',
        'cost' : 0,
        'additions': 'none',
        'status' :'released & being_prepared & order_placed'
    }
]

payments_database = [
{
        'id': 0,
        'payment type': 'card & cash',
        'payment amount': 0,
        'card details': "none",
        'status': 'cancel'
    }
]

@app.route('/')
def hello_world():
    return 'Hello Flask!'

@app.route('/proj/api/v0.1/Orders/all', methods=['GET'])
def get_all_orders():
    order = filter(lambda t: t['status'] in order_status_list , orders_database)
    order = list(order)
    return jsonify({'orders': order})
@app.route('/proj/api/v0.1/Orders', methods=['GET','POST'])
def get_orders():
    if request.method == 'POST':

        parser = reqparse.RequestParser()
        parser.add_argument('type_coffee',type=str,required=True)
        parser.add_argument('additions')
        args = parser.parse_args()
        type_coffee = args.get('type_coffee')
        additions = args.get('additions')
        if type_coffee not in cost_dic:
            return jsonify(type_coffee=False), 404
        id = orders_database[-1]['id'] + 1
        neworder = {
            'id': id,
            'type of coffee': type_coffee,
            'cost': cost_dic[type_coffee],
            'additions': additions,
            'status': "order_placed"
        }
        orders_database.append(neworder)
        newpayment = {
          'id': id,
          'payment type': 'unknown',
          'payment amount': cost_dic[type_coffee],
          'card details': "none",
          'status': 'unpaid'
        }
        payments_database.append(newpayment)
        return jsonify('/proj/api/v0.1/Payment/'+str(id))

    else:
        parser = reqparse.RequestParser()
        parser.add_argument('status', type=str)
        args = parser.parse_args()
        status = args.get('status')
        if status:
            if status in order_status_list:
                task = filter(lambda t: t['status'] == status, orders_database)
                order = list(task)
                return jsonify({'task': order})
            else:
                return jsonify('unknown status'), 404
        else:
            order = filter(lambda t: t['status'] in order_status_list and t['status'] != 'released' , orders_database)
            order = list(order)
            return jsonify({'orders': order})


@app.route('/proj/api/v0.1/Orders/<int:task_id>', methods=['GET'])
def get_order(task_id):
    task = filter(lambda t: t['id'] == task_id, orders_database)
    order = list(task)
    if len(order) == 0:
        return jsonify(id=False), 404
    return jsonify({'task': order})

@app.route('/proj/api/v0.1/Orders/<int:task_id>', methods=['PUT'])
def update_task(task_id):

    order = filter(lambda t: t['id'] == task_id, orders_database)
    order = list(order)
    if len(order) == 0:
        return jsonify(id=False), 404
    parser = reqparse.RequestParser()
    parser.add_argument('type_coffee', type=str)
    parser.add_argument('additions', type=str)
    parser.add_argument("status", type=str)
    args = parser.parse_args()
    type_coffee = args.get('type_coffee')
    additions = args.get('additions')
    status = args.get('status')
    payment = filter(lambda t: t['id'] == task_id, payments_database)
    payment = list(payment)
    if len(payment) == 0:
        return jsonify(id=False), 404
    if status:
        if status not in order_status_list:
            return jsonify('unknown status'), 404
        if type_coffee or additions:
            return jsonify('can not update'), 404
        if process_dic[order[0]['status']] != status:
            return jsonify('can not jump the status'), 404
        if status =='released' and payment[0]['status'] == 'unpaid':
            return jsonify('unpaid, can not release'), 404
        order[0]['status'] = status

    else:
        if order[0]['status'] != 'order_placed' or payment[0]['status'] != 'unpaid':
            return jsonify('can not update at this status'), 404
        if type_coffee:
            order[0]['type of coffee'] = type_coffee
            order[0]['cost'] = cost_dic[type_coffee]
            payment[0]['payment amount'] = cost_dic[type_coffee]
        if additions :
            order[0]['additions'] = additions
    return jsonify({'task': order})
    # if status and status not in order_status_list:
    #     return jsonify('unknown status'), 404
    # if order[0]['status'] != 'order_placed' or payment[0]['status'] != 'unpaid':
    #     if type_coffee or additions:
    #         return jsonify('can not update'), 404
    #     if status:
    #         order[0]['status'] = status
    #         return jsonify({'task': order})
    # if type_coffee:
    #     order[0]['type of coffee'] = type_coffee
    #     order[0]['cost'] = cost_dic[type_coffee]
    #     payment[0]['payment amount'] = cost_dic[type_coffee]
    # if additions :
    #     order[0]['additions'] = additions
    # if status:
    #     order[0]['status'] = status
    # return jsonify({'task': order})
@app.route('/proj/api/v0.1/Orders/Cancel/<int:task_id>', methods=['PUT'])
def cancel_task(task_id):
    order = filter(lambda t: t['id'] == task_id, orders_database)
    order = list(order)
    payment = filter(lambda t: t['id'] == task_id, payments_database)
    payment = list(payment)
    if len(payment) == 0:
        return jsonify(id=False), 404
    if len(order) == 0:
        return jsonify(id=False), 404
    if payment[0]['status'] == 'unpaid':
        payment[0]['status'] = 'cancel'
        order[0]['status'] = 'cancel'
    else:
        return jsonify('cancel rejected'), 404
    return jsonify({'task': order}), 200

@app.route('/proj/api/v0.1/Payment/<int:task_id>', methods=['POST'])
def create_payments(task_id):
    payment = filter(lambda t: t['id'] == task_id, payments_database)
    payment = list(payment)

    if len(payment) == 0:
        return jsonify(id=False), 404
    parser = reqparse.RequestParser()
    parser.add_argument('payment_type', type=str, required=True)
    parser.add_argument('card_detail', type=str)
    parser.add_argument('status', type=str, required=True)
    args = parser.parse_args()
    payment_type = args.get('payment_type')

    if payment_type != 'card' and payment_type != 'cash':
        return jsonify(payment_type=False), 404
    payment[0]['payment type'] = payment_type
    card_detail = args.get('card_detail')
    status = args.get('status')
    if payment_type =='card':
        payment[0]['card details'] = card_detail

    if status not in payment_status_list:
        return jsonify('unkonwn status'), 404
    payment[0]['status'] = status
    order = filter(lambda t: t['id'] == task_id, orders_database)
    order = list(order)
    order[0]['status'] = status
    return jsonify({'payment': payment})

# @app.route('/proj/api/v0.1/Orders/<int:task_id>', methods=['DELETE'])
# def delete_task(task_id):
#     task = filter(lambda t: t['id'] == task_id, tasks)
#     if len(task) == 0:
#         abort(404)
#     tasks.remove(task[0])
#     return jsonify({'result':True})

@app.route('/proj/api/v0.1/Payment', methods=['GET'])
def get_payments():
    parser = reqparse.RequestParser()
    parser.add_argument('status', type=str)
    args = parser.parse_args()
    status = args.get('status')
    if status:
        if status in payment_status_list:
            task = filter(lambda t: t['status'] == status, payments_database)
            payment = list(task)
            return jsonify({'task': payment})
        else:
            return jsonify('unknown status'), 404
    else:
        task = filter(lambda t: t['status'] != 'cancel', payments_database)
        payment = list(task)
        return jsonify({'payments': payment})

@app.route('/proj/api/v0.1/Payment/<int:task_id>', methods=['GET'])
def get_payment(task_id):
    task = filter(lambda t: t['id'] == task_id, payments_database)
    payment = list(task)
    if len(payment) == 0:
        return jsonify(id=False), 404
    return jsonify({'task': payment})

if __name__ == '__main__':
    app.run()
